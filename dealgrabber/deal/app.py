from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from driver_utils import get_driver, return_driver_to_pool

class ProductInfo:
    def __init__(self):
        self.productname = ""
        self.price = None
        self.link = None
        self.shoesize = 0
        self.driver = get_driver()
    
    def search_product(self, productname):
        self.productname = productname
        self.driver.get("https://www.flipkart.com/")
        
        try:
            search_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]'))
            )
            search_input.send_keys(self.productname)
            search_input.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Error during search: {e}")
    
    def get_product(self):
        top_results = []
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-id]"))
            )
            result = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")
        except Exception as e:
            print(f"Error fetching product elements: {e}")
            return []
        
        for i in range(min(5, len(result))):
            d = result[i].get_attribute("outerHTML")
            soup = BeautifulSoup(d, "lxml")
            
            link_tag = soup.find("a")
            link = f"https://www.flipkart.com{link_tag['href']}" if link_tag and link_tag.get("href") else None
            
            title_tag = soup.find("a", title=True)
            title = title_tag["title"] if title_tag else "No Title"
            
            price_tag = soup.find("div", string=lambda text: text and "₹" in text)
            price = price_tag.get_text(strip=True) if price_tag else "SOLD OUT"
            
            image_tag = soup.find("img")
            image_link = image_tag["src"] if image_tag and image_tag.get("src") else None
            
            top_results.append({
                "price": price,
                "link": link,
                "title": title,
                "image_link": image_link,
                "shoesize": self.shoesize
            })
        
        return top_results
    
    def close_driver(self):
        return_driver_to_pool(self.driver)
