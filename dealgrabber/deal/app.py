import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_driver():
    """Set up Chrome WebDriver with headless options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")  # Helps in cloud environments
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevents crashes in containers
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

class ProductInfo:
    def __init__(self):
        self.productname=""
        self.price= None
        self.link=None
        self.shoesize=0
        self.driver = get_chrome_driver()    
    
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

    def close_driver(self):
        self.driver.quit()
