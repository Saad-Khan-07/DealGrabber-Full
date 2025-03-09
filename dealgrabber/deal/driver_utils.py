from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_driver():
    """Set up Chrome WebDriver with headless options for production environments."""
    try:
        logger.info("Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = "/usr/bin/google-chrome"  # ✅ Use correct Chrome path

        # Use the manually installed ChromeDriver 114
        service = Service("/usr/local/bin/chromedriver")  # ✅ Set ChromeDriver path explicitly
        driver = webdriver.Chrome(service=service, options=chrome_options)

        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise
