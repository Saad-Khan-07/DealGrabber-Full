import logging
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class HandlePrice:
    def __init__(self, threshold_price, link, shoesize=0):
        """Initialize the webdriver and store product details."""
        self.driver = webdriver.Chrome()
        self.threshold_price = threshold_price
        self.link = link
        self.shoesize = shoesize

    def check_price(self):
        """Check product price and return structured data."""
        try:
            logging.info(f"🔍 Checking price for: {self.link}")
            self.driver.get(self.link)
            time.sleep(2)  # Allow page to load

            # ✅ Handle shoe size selection (if applicable)
            if int(self.shoesize) > 0:
                try:
                    sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                    size_found = False
                    for size in sizelist:
                        try:
                            sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                            time.sleep(0.5)
                            sizebutton.click()  # Click on the correct size
                            time.sleep(3)  # Allow price to update
                            size_found = True
                            break  # Exit loop after clicking the correct size
                        except:
                            continue
                    
                    if not size_found:
                        logging.warning(f"❌ No size {self.shoesize} available.")

                except Exception as e:
                    logging.error(f"⚠️ Error selecting shoe size: {e}")

            # ✅ Extract product name
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, "h1")
                nametext = name.text.strip()
            except Exception:
                nametext = "Unknown Product"
                logging.warning("⚠️ Could not find product name.")

            # ✅ Extract price
            try:
                getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
                curprice = getprice.text.strip().replace("₹", "").replace(",", "")
            except Exception:
                curprice = None
                logging.warning("⚠️ Could not find the price of the product.")

            return {
                "name": nametext,
                "link": self.link,
                "price": self.threshold_price,
                "current_price": curprice if curprice else "N/A"
            }

        except Exception as e:
            logging.error(f"🚨 Error loading page: {e}")
            return {"error": str(e)}

        finally:
            self.closedriver()  # ✅ Always close the driver

    def closedriver(self):
        """Close the WebDriver properly."""
        if self.driver:
            self.driver.quit()
            logging.info("✅ WebDriver closed.")

# ✅ Example Usage
if __name__ == "__main__":
    hp = HandlePrice(threshold_price=5000, link="https://example.com/product", shoesize=9)
    result = hp.check_price()
    logging.info(f"🔹 Final Result: {result}")
