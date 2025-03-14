import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api():
    """Test all API endpoints and print results"""
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    # Test companies endpoint
    print("\n2. Testing companies endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/companies")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} companies")
        if data:
            print(f"First company: {json.dumps(data[0], indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    # Test jobs endpoint
    print("\n3. Testing jobs endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/jobs")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Found {len(data)} jobs")
        if data:
            print(f"First job: {json.dumps(data[0], indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_api_scraping():
    print("\nChecking initial jobs in database...")
    try:
        response = requests.get("http://localhost:8000/api/v1/jobs")
        initial_jobs = response.json()
        print(f"Found {len(initial_jobs)} jobs initially")
    except Exception as e:
        print(f"Error checking initial jobs: {str(e)}")
        return
    
    
    print("\nTriggering job scraping via API...")
    try:
        
        response = requests.post(
            "http://localhost:8000/api/v1/jobs/scrape",
            params={"search_query": "python developer", "location": "remote", "limit": 3}
        )
        if response.status_code != 200:
            print(f"Error: API returned status {response.status_code}")
            print(response.text)
            return
            
        result = response.json()
        print(f"API response: {json.dumps(result, indent=2)}")
        
        
        print("\nWaiting for background task to complete (30 seconds)...")
        time.sleep(30)  # Give time for background task
        
       
        print("\nChecking for new jobs...")
        response = requests.get("http://localhost:8000/api/v1/jobs")
        final_jobs = response.json()
        
        new_jobs_count = len(final_jobs) - len(initial_jobs)
        print(f"Found {len(final_jobs)} jobs total ({new_jobs_count} new jobs)")
        
        if new_jobs_count > 0:
            print("\nScraping and storage successful!")
            print("Latest jobs:")
            for job in final_jobs[:3]:  # Show first 3 jobs
                print(f"- {job['title']} ({job['location']})")
        else:
            print("\nNo new jobs were added. Check server logs for errors.")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")

if __name__ == "__main__":
    test_api()
    test_api_scraping()