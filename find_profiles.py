import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_google_for_profiles(query, num_results=100):
    """Search Google for LinkedIn profiles matching a query"""
    profiles = []
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Search Google for LinkedIn profiles
        search_query = f"site:linkedin.com/in/ {query}"
        driver.get("https://www.google.com")
        
        # Accept cookies if prompted
        try:
            driver.find_element(By.XPATH, "//button[contains(text(), 'Accept all')]").click()
            time.sleep(1)
        except:
            pass
            
        # Enter search query
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        # Extract LinkedIn profile URLs from results
        page_num = 0
        while len(profiles) < num_results and page_num < 10:  # Limit to 10 pages
            links = driver.find_elements(By.CSS_SELECTOR, "a")
            for link in links:
                href = link.get_attribute("href")
                if href and "linkedin.com/in/" in href and "?" not in href:
                    profiles.append(href)
                    print(f"Found profile: {href}")
                    
                    if len(profiles) >= num_results:
                        break
            
            # Try to go to next page
            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
                page_num += 1
                time.sleep(random.randint(2, 5))
            except:
                break
                
    except Exception as e:
        logging.error(f"Error searching Google: {str(e)}")
    finally:
        driver.quit()
        
    # Remove duplicates and limit to requested number
    unique_profiles = list(dict.fromkeys(profiles))
    return unique_profiles[:num_results]

def save_profiles_to_csv(profiles, filename="linkedin_profiles.csv"):
    """Save LinkedIn profile URLs to CSV file"""
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Profile URL"])
            for url in profiles:
                writer.writerow([url])
        print(f"✓ Saved {len(profiles)} profile URLs to {filename}")
    except Exception as e:
        logging.error(f"Error saving to CSV: {str(e)}")

if __name__ == "__main__":
    search_terms = ["software engineer", "data scientist", "product manager"]
    all_profiles = []
    
    for term in search_terms:
        print(f"\nSearching for: {term}")
        profiles = search_google_for_profiles(term, num_results=35)
        all_profiles.extend(profiles)
        print(f"Found {len(profiles)} profiles for '{term}'")
        time.sleep(random.randint(20, 30))  # Delay between searches
    
    print(f"\nTotal unique profiles found: {len(all_profiles)}")
    save_profiles_to_csv(all_profiles)