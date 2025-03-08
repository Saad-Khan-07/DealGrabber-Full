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

        # Explicitly set Chrome and ChromeDriver paths
        chrome_path = "/usr/bin/google-chrome"
        chromedriver_path = "/usr/bin/chromedriver"

        chrome_options.binary_location = chrome_path  # ✅ Set Chrome binary path

        # Check if running in Railway.app
        if os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("RAILWAY_SERVICE_ID"):
            logger.info("Running in Railway environment")

            if os.path.exists(chrome_path) and os.path.exists(chromedriver_path):
                logger.info(f"Using system Chrome at: {chrome_path}")
                logger.info(f"Using system ChromeDriver at: {chromedriver_path}")

                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                return driver
            else:
                logger.warning("Chrome/ChromeDriver not found, falling back to WebDriverManager")

        # Standard ChromeDriverManager approach for development
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        logger.info("Chrome WebDriver initialized successfully")
        return driver

    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
        raise
