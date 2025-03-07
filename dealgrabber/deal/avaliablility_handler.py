from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

class CheckAvailability:
    def __init__(self, link, shoesize=0):
        self.link = link
        self.shoesize = shoesize
        self.name = "name"
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.binary_location = "/usr/bin/chromium"
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.available = False

    def check_availability(self):
        self.driver.get(self.link)
        time.sleep(1)
        shoe_size_found = False

        if int(self.shoesize) > 0:
            try:
                sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                if not sizelist:
                    return
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        time.sleep(0.5)
                        sizebutton.click()
                        time.sleep(5)
                        shoe_size_found = True
                        break
                    except NoSuchElementException:
                        continue
                if not shoe_size_found:
                    return
            except NoSuchElementException:
                return

        name = self.driver.find_element(By.CSS_SELECTOR, "h1")
        nametext = name.text.strip()
        getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
        curprice = getprice.text.strip().replace("₹", "").replace(",", "")

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

        if is_sold_out:
            self.available = False
        elif is_coming_soon:
            self.available = False
        else:
            self.available = True
        
        return {"name": nametext, "link": self.link, "price": curprice, "availability": self.available}
    
    def close_driver(self):
        self.driver.close()
