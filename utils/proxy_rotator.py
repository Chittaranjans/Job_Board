# utils/proxy_rotator.py
import random
import logging
import requests

class ProxyRotator:
    def __init__(self, proxy_file='proxies.txt'):
        self.proxy_file = proxy_file
        self.proxies = self.load_proxies(proxy_file)
        self.current_index = 0
        self.working_proxies = []

    def load_proxies(self, file_path):
        proxies = []
        try:
            with open(file_path, 'r') as file:
                proxies = [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            logging.error(f"Proxy file {file_path} not found.")
        return proxies

    def get_next_proxy(self):
        # Try to get working proxies if none available
        if not self.working_proxies:
            self.refresh_working_proxies()
            
        if not self.working_proxies:
            logging.error("No working proxies available")
            return None
            
        # Rotate through working proxies
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy

    def refresh_working_proxies(self):
        self.working_proxies = []
        for proxy in self.proxies:
            if self.test_proxy(proxy):
                self.working_proxies.append(proxy)
                if len(self.working_proxies) >= 5:  # Keep at least 5 working proxies
                    break

    def test_proxy(self, proxy):
        try:
            test_url = 'https://www.linkedin.com'
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/134.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            response = requests.get(
                test_url,
                proxies=proxies,
                headers=headers,
                timeout=10,
                verify=False
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logging.debug(f"Proxy {proxy} failed: {str(e)}")
            return False

    def filter_working_proxies(self):
        self.proxies = [proxy for proxy in self.proxies if self.test_proxy(proxy)]
        with open(self.proxy_file, 'w') as file:
            for proxy in self.proxies:
                file.write(f"{proxy}\n")