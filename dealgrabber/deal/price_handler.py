from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class HandlePrice:
    def __init__(self, threshold_price, link, shoesize=0):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
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
            return {"name": "Unknown", "link": self.link, "price": self.threshold_price, "current_price": "N/A"}  # ✅ Safe return
        
    def closedriver(self):
        self.driver.quit()
