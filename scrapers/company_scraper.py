from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.common.exceptions import InvalidSessionIdException
import time
from typing import Dict, Optional
from database.db_handler import store_data
import random

LINKEDIN_EMAIL = 'chittaedu22@gmail.com'
LINKEDIN_PASSWORD = 'Chitta@1234'

# Random delays to mimic human behavior
def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

class CompanyScraper(BaseScraper):
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