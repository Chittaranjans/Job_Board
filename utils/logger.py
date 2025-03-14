# utils/logger.py
import logging

logging.basicConfig(
    filename='scraper.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(error):
    logging.error(f"Scraping failed: {str(error)}")