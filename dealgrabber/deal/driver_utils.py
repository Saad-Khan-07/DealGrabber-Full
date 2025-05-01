from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import queue
import threading
import os

# Maximum number of WebDriver instances in the pool
MAX_POOL_SIZE = 3
driver_pool = queue.Queue(maxsize=MAX_POOL_SIZE)
pool_lock = threading.Lock()

def create_driver():
    """Creates a new WebDriver instance with optimized settings."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")  # Disable image loading for faster scraping
    
    # Get the ChromeDriver path from environment variable or use the default system path
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")
    
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_driver():
    """Fetches a WebDriver instance from the pool or creates a new one if needed."""
    try:
        with pool_lock:
            try:
                return driver_pool.get(block=False)  # Fetch driver from pool
            except queue.Empty:
                return create_driver()  # Create a new driver if pool is empty
    except Exception as e:
        import traceback
        stack_trace = traceback.format_exc()
        print(f"Error getting driver: {e}")
        print(f"Stack trace: {stack_trace}")
        raise  # Re-raise the exception after logging

def return_driver_to_pool(driver):
    """Returns a WebDriver instance to the pool for reuse."""
    with pool_lock:
        try:
            if driver_pool.qsize() < MAX_POOL_SIZE:
                driver_pool.put(driver)  # Return to pool
            else:
                driver.quit()  # Close excess drivers
        except:
            driver.quit()  # Ensure driver is closed in case of failure

def close_all_drivers():
    """Closes all WebDriver instances in the pool."""
    with pool_lock:
        while not driver_pool.empty():
            driver = driver_pool.get()
            driver.quit()