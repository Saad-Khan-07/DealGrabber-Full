from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dealgrabber.deal.driver_utils import get_chrome_driver

class HandlePrice:
    def __init__(self, threshold_price, link, shoesize=0):
        self.driver = get_chrome_driver()
        self.threshold_price = threshold_price
        self.link = link
        self.shoesize = shoesize
    
    def check_price(self):
        self.driver.get(self.link)

        if int(self.shoesize) > 0:
            try:
                sizelist = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]"))
                )
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        sizebutton.click()
                        WebDriverWait(self.driver, 5).until(EC.staleness_of(sizebutton))  # Wait for page refresh
                        break
                    except:
                        continue
            except Exception as e:
                print(f"No {self.shoesize} available for this shoe")

        try:
            name = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            ).text.strip()

            getprice = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '₹')]"))
            )
            curprice = getprice.text.strip().replace("₹", "").replace(",", "")
            
            return {"name": name, "link": self.link, "price": self.threshold_price, "current_price": curprice}

        except Exception as e:
            print("Couldn't find the price of the element")
            return {"name": "Unknown", "link": self.link, "price": self.threshold_price, "current_price": "N/A"}
        
    def closedriver(self):
        self.driver.quit()
