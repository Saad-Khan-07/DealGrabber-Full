from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from dealgrabber.deal.driver_utils import get_driver, return_driver_to_pool

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
            
            # Link extraction - this works in both layouts
            link_tag = soup.find("a")
            link = f"https://www.flipkart.com{link_tag['href']}" if link_tag and link_tag.get("href") else None
            
            # Title extraction - try both methods
            # Method 1: Using title attribute
            title_tag = soup.find("a", title=True)
            title = title_tag["title"] if title_tag else None
            
            # Method 2: Using class KzDlHZ if Method 1 fails
            if not title:
                title_div = soup.find("div", class_="KzDlHZ")
                title = title_div.get_text(strip=True) if title_div else "No Title"
            
            # Price extraction - try both methods
            # Method 1: Using string lambda to find ₹
            price_tag = soup.find("div", string=lambda text: text and "₹" in text)
            price = price_tag.get_text(strip=True) if price_tag else None
            
            # Method 2: Using specific class names if Method 1 fails
            if not price:
                price_div = soup.find("div", class_="Nx9bqj")
                if price_div:
                    price = price_div.get_text(strip=True)
                else:
                    # Try another common price class
                    price_div = soup.find("div", class_="_30jeq3")
                    price = price_div.get_text(strip=True) if price_div else "SOLD OUT"
            
            # Image extraction - this usually works in both layouts
            image_tag = soup.find("img")
            image_link = image_tag["src"] if image_tag and image_tag.get("src") else None
            
            # If we still don't have an image, try to find it in a different structure
            if not image_link:
                img_div = soup.find("div", class_="_4WELSP")
                if img_div:
                    img = img_div.find("img")
                    image_link = img["src"] if img and img.get("src") else None
            
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
