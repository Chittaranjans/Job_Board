from scrapers.profile_scraper import ProfileScraper
from database.db_handler import get_db
from database.model import UserProfile
import logging
import time
import random
import os
import sys
from typing import List, Dict
import argparse
import csv
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('profile_scraping.log'),
        logging.StreamHandler()
    ]
)


should_exit = False

def signal_handler(sig, frame):
    """Handle Ctrl+C to exit gracefully"""
    global should_exit
    print("\n🛑 Graceful shutdown initiated. Completing current profile...")
    should_exit = True

signal.signal(signal.SIGINT, signal_handler)

def get_profile_urls(source_type: str, source_path: str = None, search_terms: List[str] = None, count: int = 100) -> List[str]:
    """Get a list of LinkedIn profile URLs from file or by searching"""
    if source_type == "file" and source_path:
        return load_urls_from_file(source_path, count)
    else:
        
        base_urls = [
            "https://www.linkedin.com/in/williamhgates/",
            "https://www.linkedin.com/in/satyanadella/",
            "https://www.linkedin.com/in/jeffweiner08/",
            "https://www.linkedin.com/in/andrewyng/",
            "https://www.linkedin.com/in/elonmusk/",
            "https://www.linkedin.com/in/sundar-pichai-762a3b5b/",
            "https://www.linkedin.com/in/timcook/",
            "https://www.linkedin.com/in/chittaranjan18/"  # From your test file
        ]
        
       
        urls = []
        for i in range(min(count, 100)):
            if i < len(base_urls):
                urls.append(base_urls[i])
            else:
                
                random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
                urls.append(f"https://www.linkedin.com/in/{random_id}/")
        
        return urls[:count]

def load_urls_from_file(file_path: str, count: int) -> List[str]:
    """Load LinkedIn profile URLs from a CSV or text file"""
    urls = []
    try:
        with open(file_path, 'r') as file:
            if file_path.endswith('.csv'):
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].startswith("https://www.linkedin.com/in/"):
                        urls.append(row[0])
                        if len(urls) >= count:
                            break
            else:
                for line in file:
                    line = line.strip()
                    if line and line.startswith("https://www.linkedin.com/in/"):
                        urls.append(line)
                        if len(urls) >= count:
                            break
    except Exception as e:
        logging.error(f"Error loading URLs from file: {str(e)}")
    
    return urls[:count]

def scrape_profiles(urls: List[str], batch_size: int = 10, delay_min: int = 60, delay_max: int = 180) -> None:
    """Scrape multiple LinkedIn profiles with careful rate limiting"""
    global should_exit
    
    scraper = ProfileScraper()
    total_scraped = 0
    total_failed = 0
    
    print(f"🚀 Starting batch scrape of {len(urls)} LinkedIn profiles")
    
    for i, url in enumerate(urls):
        if should_exit:
            print(f"🛑 Exiting after completing {total_scraped} profiles")
            break
            
        try:
            print(f"\n[{i+1}/{len(urls)}] Scraping: {url}")
            profile_data = scraper.scrape_profile(url)
            
            if profile_data:
                total_scraped += 1
                print(f"✓ Successfully scraped: {profile_data.get('name', 'Unknown')} - {profile_data.get('headline', 'No headline')}")
                
                # Display some key data points
                if 'experience' in profile_data:
                    exp_count = len(profile_data['experience'])
                    print(f"  📋 Experience: {exp_count} positions")
                    
                if 'education' in profile_data:
                    edu_count = len(profile_data['education'])
                    print(f"  🎓 Education: {edu_count} entries")
                
                print(f"  📍 Location: {profile_data.get('location', 'Unknown')}")
            else:
                total_failed += 1
                print(f"✗ Failed to scrape profile: {url}")
            
            # Add delay between profiles to avoid rate limiting
            if i < len(urls) - 1 and not should_exit:
                delay = random.randint(3, 8)  # Short delay between profiles in same batch
                print(f"Waiting {delay} seconds before next profile...")
                time.sleep(delay)
            
            # Add longer delay between batches
            if (i + 1) % batch_size == 0 and i < len(urls) - 1 and not should_exit:
                batch_delay = random.randint(delay_min, delay_max)
                print(f"\n🕒 Completed batch of {batch_size}. Waiting {batch_delay} seconds to avoid rate limiting...")
                
                # Show countdown
                for remaining in range(batch_delay, 0, -10):
                    if should_exit:
                        break
                    print(f"Resuming in {remaining} seconds...", end="\r")
                    time.sleep(min(10, remaining))
                print("\n")
                
        except Exception as e:
            logging.error(f"Error scraping profile {url}: {str(e)}")
            total_failed += 1
            
    # Summarize results
    print("\n=== Scraping Summary ===")
    print(f"Total profiles attempted: {len(urls)}")
    print(f"Successfully scraped: {total_scraped}")
    print(f"Failed to scrape: {total_failed}")

def check_database():
    """Check if profiles were properly stored in database"""
    try:
        db = next(get_db())
        count = db.query(UserProfile).count()
        print(f"\n📊 Database contains {count} user profiles")
        
        if count > 0:
            # Display sample profiles from database
            profiles = db.query(UserProfile).limit(5).all()
            print("\nSample profiles in database:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile.name} - {profile.headline if hasattr(profile, 'headline') else 'No headline'}")
    except Exception as e:
        logging.error(f"Error checking database: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Profile Batch Scraper")
    parser.add_argument("--count", type=int, default=10, help="Number of profiles to scrape (default: 10, max: 100)")
    parser.add_argument("--source", choices=["file", "sample"], default="sample", help="Source of profile URLs")
    parser.add_argument("--file", type=str, help="File containing LinkedIn profile URLs (CSV or text)")
    parser.add_argument("--batch", type=int, default=5, help="Batch size before long pause (default: 5)")
    parser.add_argument("--delay-min", type=int, default=60, help="Minimum delay between batches in seconds (default: 60)")
    parser.add_argument("--delay-max", type=int, default=180, help="Maximum delay between batches in seconds (default: 180)")
    
    args = parser.parse_args()
    
    # Enforce limit for safety
    count = min(args.count, 100)
    
    if args.source == "file" and not args.file:
        print("Error: --file argument is required when using --source=file")
        sys.exit(1)
    
    # Get profile URLs
    urls = get_profile_urls(args.source, args.file, None, count)
    
    if not urls:
        print("Error: No valid LinkedIn profile URLs found")
        sys.exit(1)
        
    # Start scraping
    scrape_profiles(urls, args.batch, args.delay_min, args.delay_max)
    
    # Check database
    check_database()