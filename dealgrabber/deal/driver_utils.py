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
    """Set up Chrome WebDriver with headless options for production environments."""
    try:
        logger.info("Initializing Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # For Railway.app and similar platforms
        # Check for any environment indicator that we're on Railway
        if os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("RAILWAY_SERVICE_ID"):
            logger.info("Running in Railway environment")
            try:
                # Try to use the system ChromeDriver first
                driver_path = "/usr/bin/chromedriver"
                if os.path.exists(driver_path):
                    service = Service(driver_path)
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    return driver
                else:
                    # Fall back to letting Chrome find the appropriate driver
                    driver = webdriver.Chrome(options=chrome_options)
                    return driver
            except Exception as e:
                logger.error(f"Failed with explicit path: {str(e)}")
                # Fall through to default method
        
        # Standard ChromeDriverManager approach for development
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info("Chrome WebDriver initialized successfully")
        return driver
        
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise