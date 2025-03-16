from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dealgrabber.deal.driver_utils import get_chrome_driver

class CheckAvailability:
    def __init__(self, link, shoesize=0):
        self.link = link
        self.shoesize = shoesize
        self.driver = get_chrome_driver()
        self.available = False

    def check_availability(self):
        self.driver.get(self.link)
        wait = WebDriverWait(self.driver, 10)

        shoe_size_found = False
        if int(self.shoesize) > 0:
            try:
                sizelist = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]"))
                )
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        sizebutton.click()
                        shoe_size_found = True
                        break
                    except NoSuchElementException:
                        continue
            except TimeoutException:
                pass

        try:
            name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))).text.strip()
            price = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '₹')]"))
            ).text.strip().replace("₹", "").replace(",", "")
        except TimeoutException:
            return {"name": "Unknown", "link": self.link, "price": "N/A", "availability": False}

        is_sold_out = self._check_text_presence("Sold Out")
        is_coming_soon = self._check_text_presence("Coming Soon")

        self.available = not (is_sold_out or is_coming_soon)

        return {"name": name, "link": self.link, "price": price, "availability": self.available}

    def _check_text_presence(self, text):
        try:
            self.driver.find_element(By.XPATH, f"//div[contains(text(), '{text}')]")
            return True
        except NoSuchElementException:
            return False

    def close_driver(self):
        self.driver.quit()
