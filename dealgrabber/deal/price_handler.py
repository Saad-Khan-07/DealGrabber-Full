from selenium.webdriver.common.by import By
import time
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
                sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        time.sleep(0.5)
                        sizebutton.click()
                        time.sleep(5)
                        break
                    except:
                        continue
            except Exception as e:
                print(f"No {self.shoesize} available for this shoe")
                print(e)

        try:
            name = self.driver.find_element(By.CSS_SELECTOR, "h1")
            nametext = name.text.strip()

            getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
            curprice = getprice.text.strip().replace("₹", "").replace(",", "")
            
            return {"name": nametext, "link": self.link, "price": self.threshold_price, "current_price": curprice}
        
        except Exception as e:
            print("Couldn't find the price of the element")
            print(e)
            return {"name": "Unknown", "link": self.link, "price": self.threshold_price, "current_price": "N/A"}
        
    def closedriver(self):
        self.driver.quit()