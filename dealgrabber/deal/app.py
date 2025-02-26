import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class ProductInfo:
    def __init__(self):
        self.productname=""
        self.price= None
        self.link=None
        self.shoesize=0
        self.driver = webdriver.Chrome()    
    
    def search_product(self):
        self.driver.get(f"https://www.flipkart.com/")
        time.sleep(1)
        self.productname= input("enter the product you want to search: ")
        searchinput = self.driver.find_element(By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]')
        searchinput.send_keys(self.productname)
        searchinput.send_keys(Keys.RETURN)
        self.driver.implicitly_wait(5)
    
    def get_product(self):
        result = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
        d= result[0].get_attribute("outerHTML")
        soup= BeautifulSoup(d, "html.parser")
        link_tag= soup.find("a")
        if link_tag and link_tag.get("href"):
            full_link= "https://www.flipkart.com" + link_tag["href"]
            print(full_link)
            self.link=full_link
        price_tag= soup.find(class_="Nx9bqj")
        self.price = price_tag.get_text(strip=True)
        description_tag= soup.find("ul")
        if description_tag:
            description_all= description_tag.find_all("li")
            for i in description_all:
                d_elem = i.get_text(strip=True)
                print(d_elem)
        print("------------------------------------------------------")
        
        return {"price": self.price, "link": self.link, "shoesize":self.shoesize}

    # def check_shoes(self, results):
    #     for elem in results:
    #         data_id = elem.get_attribute("data-id")  # Get 'data-id' for each result
    #         if data_id and data_id.startswith("SH"):
    #             choice = input("Are you looking for shoes? (y/n): ").strip().lower()
    #             if choice == "y":
    #                 self.shoesize = int(input("Enter the size of the shoes (UK): "))
    #             break  # Exit loop after the first valid shoe product

    def close_driver(self):
        self.driver.quit()

# if __name__=="__main__":
#     pinfo= ProductInfo()
#     pinfo.search_product()
#     dinfo= pinfo.get_product()
#     print(dinfo)
