import requests
import logging
from utils.proxy_rotator import ProxyRotator

# Configure logging
logging.basicConfig(filename='proxy_test.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def test_proxy(proxy):
    try:
        response = requests.get('https://www.google.com', proxies={'http': proxy, 'https': proxy}, timeout=10)
        if response.status_code == 200:
            logging.info(f"Proxy {proxy} is working.")
            print(f"Proxy {proxy} is working.")
        else:
            logging.error(f"Proxy {proxy} failed with status code {response.status_code}.")
            print(f"Proxy {proxy} failed with status code {response.status_code}.")
    except Exception as e:
        logging.error(f"Proxy {proxy} failed with error: {str(e)}")
        print(f"Proxy {proxy} failed with error: {str(e)}")

def main():
    proxy_rotator = ProxyRotator('proxies.txt')
    proxies = proxy_rotator.proxies
    
    for proxy in proxies:
        test_proxy(proxy)

if __name__ == "__main__":
    main()