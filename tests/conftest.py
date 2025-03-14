import pytest
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
def pytest_sessionstart(session):
    """Add project root to Python path at start of session"""
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

def pytest_configure():
    """Configure test environment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create necessary directories
    Path('./chrome_profiles').mkdir(parents=True, exist_ok=True)
    Path('./logs').mkdir(parents=True, exist_ok=True)

def pytest_sessionfinish():
    """Clean up after tests"""
    os.system("taskkill /F /IM chrome.exe 2>nul")
    os.system("taskkill /F /IM chromedriver.exe 2>nul")