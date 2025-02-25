from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import time
# from deal.app import ProductInfo
from selenium.common.exceptions import NoSuchElementException

class CheckAvailability:
    def __init__(self, link, shoesize=0):
        self.link= link
        self.shoesize= shoesize
        self.name= "name"
        self.driver= webdriver.Chrome()
        self.available=False

    def check_availability(self):
        self.driver.get(self.link)
        time.sleep(1)
        shoe_size_found = False
        if int(self.shoesize)>0:
            try:
                sizelist = self.driver.find_elements(By.XPATH, "//li[contains(@id, 'swatch') and contains(@id, '-size')]")
                sizeoption=True
                if not sizelist:
                    print("No size options available for this product.")
                    sizeoption=False
                    # Exit early
                if sizeoption:
                    for size in sizelist:
                        try:
                            sizebutton = size.find_element(By.XPATH, f".//a[contains(text(), '{self.shoesize}')]")
                            time.sleep(0.5)
                            sizebutton.click()  # Click on the correct size
                            time.sleep(5)
                            shoe_size_found = True  # Mark that the size exists
                            break  # Exit loop after clicking the correct size
                        except NoSuchElementException:
                            continue  # Continue if the specific size is not found
                    
                    if not shoe_size_found:
                        print(f"Shoe size {self.shoesize} is not available.")
                        return  # Exit early to prevent false availability messages

            except NoSuchElementException:
                print(f"No size {self.shoesize} available for this shoe.")
                return  # Exit early

        name = self.driver.find_element(By.CSS_SELECTOR, "h1")
        nametext= name.text.strip()
        getprice = self.driver.find_element(By.XPATH, "//div[contains(text(), '₹')]")
        curprice= getprice.text.strip().replace("₹","").replace(",","")

        # Check if the product is sold out
        is_sold_out = False
        is_coming_soon = False

        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Sold Out')]")
            is_sold_out = True
        except NoSuchElementException:
            pass  # If not found, ignore

        try:
            self.driver.find_element(By.XPATH, "//div[contains(text(), 'Coming Soon')]")
            is_coming_soon = True
        except NoSuchElementException:
            pass  # If not found, ignore

        # Decision Making
        if is_sold_out:
            self.available=False
            print("The product is sold out. I'll notify you when it's available.")
        elif is_coming_soon:
            self.available=False
            print("The product hasn't come on the platform yet! I'll notify you when it's available.")
        else:
            self.available=True
            print("The product is available!")
        return {"name": nametext, "link": self.link, "price": curprice, "availability": self.available}
        

    def close_driver(self):
        self.driver.close()


# if __name__=="__main__":
#     pinfo= ProductInfo()
#     pinfo.search_product()
#     dinfo= pinfo.get_product()
#     print(dinfo)
#     # pi= ProductInfo()
#     ca = CheckAvailability(dinfo["link"],  dinfo["shoes"])
#     ca.check_availability()
#     ca.close_driver()