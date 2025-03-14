from setuptools import setup, find_packages

setup(
    name="joblo_scraping",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'selenium',
        'webdriver_manager',
        'pytest',
        'sqlalchemy'
    ]
)