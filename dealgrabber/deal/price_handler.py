import logging
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time

# Configure logging
logging.basicConfig(filename='example1.log', encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CheckAvailability:
    def __init__(self, link, shoesize=0):
        self.link = link
        self.shoesize = shoesize
        self.name = "name"
        self.driver = webdriver.Chrome()
        self.available = False

    def check_availability(self):
        logging.info(f"Checking availability for link: {self.link} with shoe size: {self.shoesize}")
        self.driver.get(self.link)
        time.sleep(1)
        shoe_size_found = False

        if int(self.shoesize) > 0:
            try:
                sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                if not sizelist:
                    logging.warning("No size options available for this product.")
                    return
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        time.sleep(0.5)
                        sizebutton.click()  # Click on the correct size
                        time.sleep(5)
                        shoe_size_found = True  # Mark that the size exists
                        break  # Exit loop after clicking the correct size
                    except NoSuchElementException:
                        continue
                if not shoe_size_found:
                    logging.warning(f"Shoe size {self.shoesize} is not available.")
                    return
            except NoSuchElementException:
                logging.error(f"No size {self.shoesize} available for this shoe.")
                return

        name = self.driver.find_element(By.CSS_SELECTOR, "h1")
        nametext = name.text.strip()
        getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
        curprice = getprice.text.strip().replace("₹", "").replace(",", "")

        # Check if the product is sold out
        is_sold_out = False
        is_coming_soon = False

        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Sold Out')]")
            is_sold_out = True
        except NoSuchElementException:
            pass

        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Coming Soon')]")
            is_coming_soon = True
        except NoSuchElementException:
            pass

        # Decision Making
        if is_sold_out:
            self.available = False
            logging.info("The product is sold out. Notification will be sent when it's available.")
        elif is_coming_soon:
            self.available = False
            logging.info("The product hasn't been launched yet! Notification will be sent when available.")
        else:
            self.available = True
            logging.info("The product is available!")
        
        return {"name": nametext, "link": self.link, "price": curprice, "availability": self.available}
    
    def close_driver(self):
        logging.info("Closing the browser driver.")
        self.driver.close()
