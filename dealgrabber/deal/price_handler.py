from selenium.webdriver.common.by import By
from selenium import webdriver
import time

class HandlePrice:
    def __init__(self, threshold_price, link, shoesize=0):
        self.driver= webdriver.Chrome()
        self.threshold_price= threshold_price
        self.link= link
        self.shoesize= shoesize
    
    def check_price(self):
        self.driver.get(self.link)
        if(int(self.shoesize)>0):
            try:
                sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                for size in sizelist:
                    try:
                        sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                        time.sleep(0.5)
                        sizebutton.click()  # Click on the correct size
                        time.sleep(5)
                        break  # Exit loop after clicking the correct size
                    except:
                        continue
            except Exception as e:
                print(f"no {self.shoesize} available for this shoe")
                print(e)
        name = self.driver.find_element(By.CSS_SELECTOR, "h1")
        nametext= name.text.strip()
        try:
            getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
            curprice= getprice.text.strip().replace("₹","").replace(",","")
            return {"name": nametext, "link": self.link, "price": self.threshold_price, "current_price": curprice}
        except Exception as e:
            print("couldnt find the price of the element")
            print(e)
        
    def closedriver(self):
        self.driver.close()
    





# if __name__=="__main__":    
#     shoes = {"shoesize": 9,"shoes": True}
#     threshold_price=5000
#     link="https://www.flipkart.com/puma-rungryp-sneakers-men/p/itm7b4744135bc9c?pid=SHOGQAZD7MVX94YU&lid=LSTSHOGQAZD7MVX94YURTWUXM&marketplace=FLIPKART&q=puma+shoes&store=osp&srno=s_1_3&otracker=search&otracker1=search&fm=Search&iid=f2d678a8-fab2-47a9-adfc-860f6007712b.SHOGQAZD7MVX94YU.SEARCH&ppt=sp&ppn=sp&ssid=fx5xfr2k2o0000001740292012231&qH=12daa41359850f83"

#     hp= HandlePrice(8000, threshold_price, link, shoes)
#     d = hp.check_price()
#     hp.closedriver()
#     print(d)