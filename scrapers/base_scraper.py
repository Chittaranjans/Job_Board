import logging
import pickle
import os
import time
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils.proxy_rotator import ProxyRotator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

LINKEDIN_EMAIL = os.getenv('LINKEDIN_EMAIL')
LINKEDIN_PASSWORD = os.getenv('LINKEDIN_PASSWORD')

# Only define once
def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))
    
class BaseScraper:
    def __init__(self):
        # Fix proxy path
        proxy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'proxies.txt')
        self.proxy_pool = ProxyRotator(proxy_path)
        self.driver = None
        self.session_cookies = None

        # Create chrome profile directory properly
        chrome_profile_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chrome_profile')
        Path(chrome_profile_path).mkdir(parents=True, exist_ok=True)
        self.chrome_profile_path = chrome_profile_path
        logging.info(f"Chrome profile directory created at {chrome_profile_path}")

        # Add configuration options
        self.config = {
            'timeout': 30,
            'scroll_pause': 2,
            'retry_delay': 5,
            'max_retries': 3
        }

    def save_cookies(self):
        if self.driver:
            cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'linkedin_cookies.pkl')
            try:
                with open(cookie_path, 'wb') as f:
                    pickle.dump(self.driver.get_cookies(), f)
                    logging.debug(f"Cookies saved to {cookie_path}")
            except Exception as e:
                logging.error(f"Failed to save cookies: {str(e)}")

    def load_cookies(self):
        try:
            cookie_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'linkedin_cookies.pkl')
            if os.path.exists(cookie_path):
                with open(cookie_path, 'rb') as f:
                    cookies = pickle.load(f)
                    logging.debug(f"Cookies loaded from {cookie_path}")
                    return cookies
        except Exception as e:
            logging.error(f"Failed to load cookies: {str(e)}")
        return None    
    
    def get_driver(self, proxy=None, headless=False):
        try:
            # Use a direct path to chromedriver if we have one set
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = webdriver.ChromeOptions()

            # Essential anti-detection options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Performance and stability options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-extensions')
            
            if headless:
                chrome_options.add_argument('--headless=new')
            
            # Use a realistic window size
            chrome_options.add_argument('--window-size=1920,1080')
            
            # Use rotating user agents
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
            ]
            chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
            
            if proxy:
                chrome_options.add_argument(f'--proxy-server={proxy}')
            
            # Use fixed profile directory
            chrome_options.add_argument(f"--user-data-dir={self.chrome_profile_path}")
            
            # Use explicit chromedriver path if available from JobScraper
            if hasattr(self, 'chromedriver_path') and os.path.exists(self.chromedriver_path):
                service = Service(executable_path=self.chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback to automatic detection
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Further anti-detection with CDP commands
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """
            })
            
            return driver
            
        except Exception as e:
            logging.error(f"Failed to create Chrome driver: {str(e)}")
            # Try one more time with a manually downloaded driver
            try:
                # Get Windows architecture
                import platform
                is_64bits = platform.architecture()[0] == '64bit'
                
                # Set path to appropriate driver
                drivers_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'drivers')
                chromedriver_path = os.path.join(drivers_dir, 'chromedriver.exe')
                
                # Log the attempt
                logging.info(f"Attempting with local driver at {chromedriver_path}")
                
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                return driver
            except Exception as second_e:
                logging.error(f"Second attempt failed: {str(second_e)}")
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
            user_data_dir = self.chrome_profile_path
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