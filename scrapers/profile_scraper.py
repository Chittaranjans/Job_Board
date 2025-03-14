from .base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
from typing import Dict, Optional
from database.db_handler import store_data
import random
from bs4 import BeautifulSoup


# Random delays to mimic human behavior
def random_delay(min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))

class ProfileScraper(BaseScraper):
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