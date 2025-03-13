import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from dealgrabber.deal.driver_utils import get_chrome_driver

class ProductInfo:
    def __init__(self):
        self.productname=""
        self.price= None
        self.link=None
        self.shoesize=0
        self.driver = get_chrome_driver()  
    
    def search_product(self,productname):
        self.productname = productname
        self.driver.get(f"https://www.flipkart.com/")
        time.sleep(1)
        searchinput = self.driver.find_element(By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]')
        searchinput.send_keys(self.productname)
        searchinput.send_keys(Keys.RETURN) #press enter to search
        self.driver.implicitly_wait(5)
    
    def get_product(self):
        top_results = []
        result = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")

        for i in range(min(5, len(result))):  # Avoid IndexError if results < 5
            d = result[i].get_attribute("outerHTML")
            soup = BeautifulSoup(d, "html.parser")

            # ✅ Extract the main product link (First <a> tag)
            link_tag = soup.find("a", href=True)
            link = "https://www.flipkart.com" + link_tag["href"] if link_tag else None

            # ✅ Extract the product title (Second <a> tag with 'title' attribute)
            title_tag = soup.find("a", title=True)
            title = title_tag["title"] if title_tag else "N/A"

            # ✅ Find the price by looking for ₹ symbol (More stable than random class names)
            price_tag = soup.find(string=lambda text: text and "₹" in text)
            price = price_tag.strip() if price_tag else "SOLD OUT"

            # ✅ Extract the product image inside <a> tag
            image_tag = link_tag.find("img") if link_tag else None
            image_link = image_tag["src"] if image_tag and image_tag.get("src") else None

            # ✅ Extract product descriptions (inside <ul>)
            description_tag = soup.find("ul")
            descriptions = [li.get_text(strip=True) for li in description_tag.find_all("li")] if description_tag else []

            print(link, price, descriptions)
            print("------------------------------------------------------")

            top_results.append({
                "price": price,
                "link": link,
                "title": title,
                "image_link": image_link,
                "shoesize": self.shoesize
            })

        return top_results


    def close_driver(self):
        self.driver.quit()