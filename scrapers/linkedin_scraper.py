import time
import random
import logging
import pickle
import os
from pathlib import Path
import urllib3
from typing import Optional, List, Dict
from datetime import datetime
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log'),
        logging.StreamHandler()
    ]
)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException , SessionNotCreatedException
from bs4 import BeautifulSoup
from utils.proxy_rotator import ProxyRotator

from database.db_handler import store_data  # Assuming you have a store_data function in db_handler

# LinkedIn credentials (replace with your own)
LINKEDIN_EMAIL = 'chittaedu22@gmail.com'
LINKEDIN_PASSWORD = 'Chitta@1234'

# Random delays to mimic human behavior
def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

class LinkedInScraper:
    def __init__(self):
        self.proxy_pool = ProxyRotator('proxies.txt')
        self.driver = None
        self.session_cookies = None

        Path('./chrome_profile').mkdir(parents=True, exist_ok=True)
        logging.debug("Chrome profile directory created")

        # Add configuration options
        self.config = {
            'timeout': 30,
            'scroll_pause': 2,
            'retry_delay': 5,
            'max_retries': 3
        }

    def save_cookies(self):
        if self.driver:
           cookie_path = os.path.abspath('linkedin_cookies.pkl')
        with open(cookie_path, 'wb') as f:
            pickle.dump(self.driver.get_cookies(), f)
            logging.debug(f"Cookies saved to {cookie_path}")

    def load_cookies(self):
        try:
          cookie_path = os.path.abspath('linkedin_cookies.pkl')
          if os.path.exists(cookie_path):
            with open(cookie_path, 'rb') as f:
                cookies = pickle.load(f)
                logging.debug(f"Cookies loaded from {cookie_path}")
                return cookies
        except Exception as e:
            logging.error(f"Failed to load cookies: {str(e)}")
        return None    
    
    def get_driver(self, proxy=None, headless=True):
        chrome_options = Options()

        # Basic options
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Disable GPU and graphics
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-webgl')
        chrome_options.add_argument('--disable-webgl2')
        
        # Disable machine learning features
        chrome_options.add_argument('--disable-features=EnableTensorFlow,WebML')
        chrome_options.add_argument('--disable-machine-learning')
        chrome_options.add_argument('--disable-remote-fonts')
        
        # Performance options
        chrome_options.add_argument('--disable-dev-tools')
        chrome_options.add_argument('--disable-client-side-phishing-detection')
        chrome_options.add_argument('--disable-component-extensions-with-background-pages')
        
        if headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-setuid-sandbox')
            
        # Anti-detection options    
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # Use fixed profile directory instead of timestamp-based
        user_data_dir = os.path.abspath("./chrome_profile")
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        
        try:
            service = webdriver.ChromeService(
                log_output=os.path.devnull
            )
            
            driver = webdriver.Chrome(
                service=service,
                options=chrome_options
            )
            
            # Set custom user agent
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
            })
            
            return driver
            
        except Exception as e:
            logging.error(f"Failed to create Chrome driver: {str(e)}")
            raise

    def cleanup(self):
        try:
           if self.driver:
            if self.session_cookies:
                self.save_cookies()
            self.driver.quit()
            self.driver = None
        except Exception as e:
           logging.error(f"Cleanup failed: {str(e)}")

    def wait_for_page_load(self, driver, timeout=30):
        try:
          old_page = driver.find_element(By.TAG_NAME, 'html')
        
        # Wait for staleness of old page
          WebDriverWait(driver, timeout).until(
            EC.staleness_of(old_page)
          ) 
        
        # Wait for presence of body
          WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
          )
        
        # Wait for all AJAX requests to complete
          WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return jQuery.active == 0')
          )
        
          return True
        except Exception as e:
            logging.error(f"Page load timeout: {str(e)}")
        return False 
    def scrape_with_proxy(self, url, retries=3):
        for attempt in range(retries):
           proxy = self.proxy_pool.get_next_proxy()
           if not proxy:
            logging.error("No working proxies available")
            return None
            
        driver = None
        try:
            driver = self.get_driver(proxy=proxy)
            if not self.login(driver): 
                return None
            
            # Your scraping code here
            data = self.extract_data(driver)
            if data:
                return data
                
        except Exception as e:
            logging.error(f"Scraping failed with proxy {proxy}: {str(e)}")
        finally:
            if driver:
                driver.quit()
    
        return None
    def login(self, driver, retries=3):
        try:
            # First try with saved cookies
            cookies = self.load_cookies()
            if cookies:
                logging.info("Attempting login with saved cookies")
                driver.get('https://www.linkedin.com')
                for cookie in cookies:
                    driver.add_cookie(cookie)
                driver.get('https://www.linkedin.com/feed/')
                random_delay(2, 4)
                
                if "feed" in driver.current_url:
                    logging.info("Login successful with cookies")
                    return True

            # If cookies failed, try normal login
            logging.info("Attempting normal login")
            driver.get('https://www.linkedin.com/login')
            random_delay(2, 4)

            if "challenge" in driver.current_url:
                return self.handle_security_check(driver)

            # Type credentials with human-like delays
            email = driver.find_element(By.ID, 'username')
            for char in LINKEDIN_EMAIL:
                email.send_keys(char)
                random_delay(0.1, 0.3)

            password = driver.find_element(By.ID, 'password')
            for char in LINKEDIN_PASSWORD:
                password.send_keys(char)
                random_delay(0.1, 0.3)

            # Click login and wait
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            random_delay(3, 5)

            # Handle different post-login scenarios
            current_url = driver.current_url
            if "checkpoint/challenge" in current_url:
                return self.handle_security_check(driver)
            elif "feed" in current_url:
                self.session_cookies = driver.get_cookies()
                self.save_cookies()
                return True
                
            logging.error(f"Unexpected redirect after login: {current_url}")
            return False

        except Exception as e:
            logging.error(f"Login failed: {str(e)}")
            return False

    def handle_security_check(self, driver):
        try:
            verification_url = driver.current_url
            logging.info("Handling security verification...")

            # Get current capabilities and cookies
            cookies = driver.get_cookies()
            current_url = driver.current_url
            
            # Always switch to visible browser for security check
            driver.quit()
            
            # Create new visible browser with Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1200,800')  # Set explicit window size
            chrome_options.add_argument('--start-maximized')  # Maximize window
            
            # Anti-detection options    
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use existing profile directory
            user_data_dir = os.path.abspath("./chrome_profile")
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Create new visible driver
            new_driver = webdriver.Chrome(options=chrome_options)
            
            # Restore session
            new_driver.get("https://www.linkedin.com")
            for cookie in cookies:
                try:
                    new_driver.add_cookie(cookie)
                except Exception as e:
                    logging.debug(f"Failed to restore cookie: {str(e)}")
                    continue
                    
            # Go to verification page
            new_driver.get(current_url)
            
            # Update driver references
            self.driver = new_driver
            driver = new_driver

            print("\n=== SECURITY VERIFICATION REQUIRED ===")
            print("1. Complete the verification in the browser window")
            print("2. Script will continue automatically after verification")
            print("3. You have 5 minutes to complete this step")
            
            max_wait = 300  # 5 minutes timeout
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    current_url = driver.current_url
                    if "feed" in current_url:
                        logging.info("Security verification completed successfully")
                        self.session_cookies = driver.get_cookies()
                        self.save_cookies()
                        return True
                    elif "checkpoint/challenge" not in current_url:
                        if "login" not in current_url:
                            return True
                except Exception as e:
                    logging.error(f"Error checking URL: {str(e)}")
                    
                time.sleep(2)
                
            logging.error("Security verification timed out")
            return False
            
        except Exception as e:
            logging.error(f"Security check handling failed: {str(e)}")
            return False

    def scrape_company(self, url, retries=3):
        # First attempt with own IP address
        driver = self.get_driver()
        if self.login(driver):
            company_data = self.extract_company_details(driver)
            if company_data:
                store_data(company_data, 'company')
                driver.quit()
                return company_data
        driver.quit()

        # Subsequent attempts with proxies
        for attempt in range(retries):
            proxy = self.proxy_pool.get_next_proxy()
            driver = self.get_driver(proxy)
            if not self.login(driver):
                driver.quit()
                continue

            try:
                logging.debug(f"Attempting to scrape company data from {url}, attempt {attempt + 1}")
                driver.get(url)
                random_delay()

                # Extract company details
                company_data = self.extract_company_details(driver)
                if company_data:
                    store_data(company_data, 'company')
                    driver.quit()
                    return company_data

                driver.quit()
            except InvalidSessionIdException as e:
                logging.error(f"Invalid session ID: {str(e)}")
                driver.quit()
                continue
            except Exception as e:
                logging.error(f"Failed to load page with proxy {proxy}: {str(e)}")
                driver.quit()
                continue  # Try the next proxy
        return None  # Return None if all retries fail

    def extract_company_details(self, driver):
        try:
            logging.debug("Extracting company details")
            company_data = {}

            # Wait for the company name element to be present
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "org-top-card-summary__title"))
            )

            company_data['name'] = driver.find_element(By.CLASS_NAME, "org-top-card-summary__title").text.strip()

            # Click About Tab or View All Link
            navigation = driver.find_element(By.CLASS_NAME, "org-page-navigation__items ")
            try:
                self.__find_first_available_element__(
                    navigation.find_elements(By.XPATH, "//a[@data-control-name='page_member_main_nav_about_tab']"),
                    navigation.find_elements(By.XPATH, "//a[@data-control-name='org_about_module_see_all_view_link']"),
                ).click()
            except:
                driver.get(f"{driver.current_url}/about")

            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'section'))
            )
            time.sleep(3)

            grid = driver.find_element(By.CLASS_NAME, "artdeco-card.org-page-details-module__card-spacing.artdeco-card.org-about-module__margin-bottom")
            descWrapper = grid.find_elements(By.TAG_NAME, "p")
            if len(descWrapper) > 0:
                company_data['about_us'] = descWrapper[0].text.strip()

            labels = grid.find_elements(By.TAG_NAME, "dt")
            values = grid.find_elements(By.TAG_NAME, "dd")
            num_attributes = min(len(labels), len(values))

            for i in range(num_attributes):
                txt = labels[i].text.strip()
                if txt == 'Website':
                    company_data['website'] = values[i].text.strip()
                elif txt == 'Phone':
                    company_data['phone'] = values[i].text.strip()
                elif txt == 'Industry':
                    company_data['industry'] = values[i].text.strip()
                elif txt == 'Company size':
                    company_data['company_size'] = values[i].text.strip()
                elif txt == 'Headquarters':
                    company_data['headquarters'] = values[i].text.strip()
                elif txt == 'Type':
                    company_data['company_type'] = values[i].text.strip()
                elif txt == 'Founded':
                    company_data['founded'] = values[i].text.strip()
                elif txt == 'Specialties':
                    company_data['specialties'] = "\n".join(values[i].text.strip().split(", "))

            logging.debug(f"Extracted company details: {company_data}")
            return company_data
        except Exception as e:
            logging.error(f"Failed to extract company details: {str(e)}")
            return None

    def __find_first_available_element__(self, *elements):
        for element_list in elements:
            for element in element_list:
                if element.is_displayed():
                    return element
        return None

    def scrape_jobs(self, company_id, url=None, retries=3):
        driver = None
        try:
            driver = self.get_driver(headless=False)
            
            if not self.login(driver):
                logging.error("Login failed")
                return None

            # Use provided URL or default format
            job_url = url or f'https://www.linkedin.com/jobs/search/?f_C={company_id}'
            logging.info(f"Navigating to: {job_url}")
            
            driver.get(job_url)
            random_delay(3, 5)

            # Wait for job listings
            selectors = [
                ".jobs-search-results__list-item",
                ".job-card-container",
                "[data-job-id]"
            ]
            
            jobs_found = False
            for selector in selectors:
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    jobs_found = True
                    logging.info(f"Found jobs with selector: {selector}")
                    break
                except:
                    continue

            if not jobs_found:
                logging.error("No jobs found on page")
                return None

            # Scroll to load all jobs
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                random_delay(1, 2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            return self.extract_jobs_data(driver, company_id)

        except Exception as e:
            logging.error(f"Failed to scrape jobs: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()

    # Improve job extraction
    def extract_jobs_data(self, driver, company_id) -> List[Dict]:
        """Extract job listings with better error handling and validation"""
        try:
            jobs = []
            seen_jobs = set()  # Track duplicates

            # Wait for job container
            job_container = WebDriverWait(driver, self.config['timeout']).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )

            # Scroll and load all jobs
            while True:
                # Get current job cards
                job_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container")
                
                for card in job_cards:
                    try:
                        job_id = card.get_attribute("data-job-id")
                        if job_id in seen_jobs:
                            continue
                            
                        seen_jobs.add(job_id)
                        
                        # Safe click with retry
                        self._safe_action(lambda: card.click())
                        random_delay(1, 2)

                        job_data = {
                            'job_id': job_id,
                            'company_id': company_id,
                            'title': self._safe_extract(card, ".job-card-list__title"),
                            'location': self._safe_extract(card, ".job-card-container__metadata-item"),
                            'job_type': self._get_job_type(driver),
                            'experience': self._get_experience(driver),
                            'description': self._get_job_description(driver),
                            'posted_date': self._parse_posted_date(
                                self._safe_extract(card, "time")
                            ),
                            'scraped_at': datetime.now()
                        }

                        if self._validate_job_data(job_data):
                            jobs.append(job_data)
                            logging.info(f"Extracted job: {job_data['title']}")

                    except Exception as e:
                        logging.error(f"Failed to extract job card: {str(e)}")
                        continue

                # Check if we should load more
                if not self._load_more_jobs(driver):
                    break

            return jobs

        except Exception as e:
            logging.error(f"Failed to extract jobs data: {str(e)}")
            return None

    def _validate_job_data(self, job_data: Dict) -> bool:
        """Validate required job fields are present"""
        required_fields = ['title', 'company_id', 'job_id']
        return all(job_data.get(field) for field in required_fields)

    def _get_job_description(self, driver) -> Optional[str]:
        """Extract full job description"""
        try:
            desc_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-description"))
            )
            return desc_element.text.strip()
        except:
            return None

    def _safe_action(self, action, retry_count=3):
        """Safely execute selenium actions with retries"""
        for attempt in range(retry_count):
            try:
                return action()
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                if attempt == retry_count - 1:
                    raise e
                random_delay(1, 2)
                continue

    def _safe_extract(self, element, selector):
        """Safely extract text from element"""
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except:
            return None

    def _get_job_type(self, driver):
        """Extract job type from details"""
        try:
            job_type_elem = driver.find_element(
                By.CSS_SELECTOR,
                ".jobs-unified-top-card__job-insight span:contains('Employment type')"
            )
            return job_type_elem.text.replace('Employment type', '').strip()
        except:
            return None

    def _get_experience(self, driver):
        """Extract experience requirements"""
        try:
            exp_elem = driver.find_element(
                By.CSS_SELECTOR,
                ".jobs-unified-top-card__job-insight span:contains('Experience')"
            )
            return exp_elem.text.replace('Experience', '').strip()
        except:
            return None

    def _get_posted_by(self, driver):
        """Extract job poster information"""
        try:
            return driver.find_element(
                By.CSS_SELECTOR,
                ".jobs-poster__name"
            ).text.strip()
        except:
            return None

    def _parse_posted_date(self, date_text):
        """Convert LinkedIn date format to datetime"""
        from datetime import datetime, timedelta
        try:
            if not date_text:
                return datetime.now()
                
            if 'hours' in date_text or 'minutes' in date_text:
                return datetime.now()
            elif 'day' in date_text:
                days = int(date_text.split()[0])
                return datetime.now() - timedelta(days=days)
            elif 'week' in date_text:
                weeks = int(date_text.split()[0])
                return datetime.now() - timedelta(weeks=weeks)
            elif 'month' in date_text:
                months = int(date_text.split()[0])
                return datetime.now() - timedelta(days=months*30)
            return datetime.now()
        except:
            return datetime.now()

    def scrape_profile(self, profile_url, retries=3):
        # First attempt with own IP address
        driver = self.get_driver()
        if self.login(driver):
            profile_data = self.extract_profile_data(driver, profile_url)
            if profile_data:
                store_data(profile_data, 'profile')
                driver.quit()
                return profile_data
        driver.quit()

        # Subsequent attempts with proxies
        for attempt in range(retries):
            proxy = self.proxy_pool.get_next_proxy()
            driver = self.get_driver(proxy)
            if not self.login(driver):
                driver.quit()
                continue

            try:
                logging.debug(f"Attempting to scrape profile from {profile_url}, attempt {attempt + 1}")
                driver.get(profile_url)
                random_delay()

                profile_data = self.extract_profile_data(driver, profile_url)
                if profile_data:
                    store_data(profile_data, 'profile')
                    driver.quit()
                    return profile_data

                driver.quit()
            except Exception as e:
                logging.error(f"Failed to load page with proxy {proxy}: {str(e)}")
                driver.quit()
                continue  # Try the next proxy
        return None  # Return None if all retries fail

    def extract_profile_data(self, driver, profile_url):
        try:
            logging.debug(f"Attempting to scrape profile from {profile_url}")
            driver.get(profile_url)
            random_delay()

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print(soup.prettify())  # Print the HTML content for debugging

            # Extract profile data
            name_element = soup.find('h1', {'class': 'text-heading-xlarge'})
            experience_element = soup.find('.experience__list')

            if not name_element or not experience_element:
                print("Failed to find the required elements on the page.")
                logging.error("Failed to find the required elements on the page.")
                return None

            name = name_element.get_text(strip=True)
            experience = experience_element.get_text(strip=True)

            logging.debug(f"Extracted profile data: {{'name': name, 'experience': experience}}")
            return {
                'name': name,
                'experience': experience,
                # Add other fields
            }
        except Exception as e:
            logging.error(f"Failed to extract profile data: {str(e)}")
            return None