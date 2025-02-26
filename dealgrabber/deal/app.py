import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    filename="product_info.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ProductInfo:
    def __init__(self):
        """Initialize the headless Chrome driver for Selenium."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Fix shared memory issues
        chrome_options.add_argument("--log-level=3")  # Reduce log verbosity
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.productname = ""
        self.price = None
        self.link = None
        self.shoesize = 0

    def search_product(self, product_name=None):
        """Search for the product on Flipkart. Accepts an optional product name."""
        try:
            self.driver.get("https://www.flipkart.com/")
            time.sleep(2)

            if not product_name:
                product_name = input("Enter the product you want to search: ")

            self.productname = product_name
            search_input = WebDriverWait(self.driver, 10).until(
                lambda d: d.find_element(By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]')
            )
            search_input.send_keys(product_name)
            search_input.send_keys(Keys.RETURN)
            self.driver.implicitly_wait(5)
            logging.info(f"Search initiated for: {product_name}")

        except TimeoutException:
            logging.error("Search bar not found on Flipkart.")
        except Exception as e:
            logging.error(f"Unexpected error in search_product: {e}")

    def get_product(self):
        """Extract product details like link, price, and description."""
        try:
            result = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")

            if not result:
                logging.warning("No product results found.")
                return {"error": "No products found"}

            first_result_html = result[0].get_attribute("outerHTML")
            soup = BeautifulSoup(first_result_html, "html.parser")

            # Extract Product Link
            link_tag = soup.find("a")
            if link_tag and link_tag.get("href"):
                self.link = "https://www.flipkart.com" + link_tag["href"]
            else:
                self.link = None
                logging.warning("Product link not found.")

            # Extract Price
            price_tag = soup.find(class_="Nx9bqj")
            self.price = price_tag.get_text(strip=True) if price_tag else "Price not available"
            
            # Extract Description
            description_tag = soup.find("ul")
            description_text = []
            if description_tag:
                description_all = description_tag.find_all("li")
                description_text = [i.get_text(strip=True) for i in description_all]

            logging.info(f"Product found: {self.productname}, Price: {self.price}, Link: {self.link}")

            return {
                "product_name": self.productname,
                "price": self.price,
                "link": self.link,
                "shoesize": self.shoesize,
                "description": description_text
            }

        except NoSuchElementException:
            logging.error("Required elements (name, price, description) not found on Flipkart.")
            return {"error": "Failed to retrieve product details"}
        except Exception as e:
            logging.error(f"Unexpected error in get_product: {e}")
            return {"error": str(e)}

    def close_driver(self):
        """Close the Selenium WebDriver instance."""
        try:
            self.driver.quit()
            logging.info("Browser driver closed successfully.")
        except Exception as e:
            logging.error(f"Error closing driver: {e}")

# Example Usage
# if __name__ == "__main__":
#     pinfo = ProductInfo()
#     pinfo.search_product("Nike Shoes")
#     dinfo = pinfo.get_product()
#     print(dinfo)
#     pinfo.close_driver()
