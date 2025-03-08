from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_driver():
    """Set up Chrome WebDriver with headless options."""
    try:
        logger.info("Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Set binary location if environment variable exists
        chrome_binary = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
        chrome_options.binary_location = chrome_binary
        
        # Log for debugging
        logger.info(f"Chrome binary location: {chrome_binary}")
        
        # Use Chrome version as an argument if needed
        chrome_version = None
        try:
            # Try to get Chrome version, fallback gracefully if it fails
            result = os.popen(f"{chrome_binary} --version").read()
            if result:
                version_parts = result.split()
                if len(version_parts) >= 2:
                    chrome_version = version_parts[1].split('.')[0]  # Just the major version
                    logger.info(f"Detected Chrome version: {chrome_version}")
        except Exception as e:
            logger.warning(f"Could not detect Chrome version: {e}")
        
        # Initialize WebDriver with version if available
        if chrome_version:
            service = Service(ChromeDriverManager(chrome_version=chrome_version).install())
        else:
            service = Service(ChromeDriverManager().install())
            
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise