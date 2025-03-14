import os
import shutil
import pickle
import logging

def cleanup_scraper():
    """Reset scraper state by cleaning up Chrome profile and cookies"""
    try:
       
        chrome_profile = os.path.join(os.path.dirname(__file__), 'chrome_profile')
        if os.path.exists(chrome_profile):
            shutil.rmtree(chrome_profile)
            print(f"✓ Chrome profile removed")
            
       
        cookies_file = os.path.join(os.path.dirname(__file__), 'linkedin_cookies.pkl')
        if os.path.exists(cookies_file):
            os.remove(cookies_file)
            print(f"✓ Cookies file removed")
            
       
        for filename in os.listdir(os.path.dirname(__file__)):
            if filename.endswith('.png'):
                os.remove(os.path.join(os.path.dirname(__file__), filename))
                print(f"✓ Removed {filename}")
        
        print("\nScraper reset complete. Try running test_scraper.py again.")
        
    except Exception as e:
        print(f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    cleanup_scraper()