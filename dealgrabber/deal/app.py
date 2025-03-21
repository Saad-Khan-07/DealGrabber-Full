from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dealgrabber.deal.driver_utils import get_driver,return_driver_to_pool

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
        
        # Wait until search input is present
        searchinput = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]'))
        )
        
        searchinput.send_keys(self.productname)
        searchinput.send_keys(Keys.RETURN)

        # Wait until search results are loaded
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-id]"))
        )

    def get_product(self):
        top_results = []
        result = self.driver.find_elements(By.CSS_SELECTOR, "div[data-id]")

        for i in range(min(5, len(result))):  # Avoid IndexError if results < 5
            d = result[i].get_attribute("outerHTML")
            soup = BeautifulSoup(d, "lxml")  # ✅ Faster parsing using lxml

            link_tag = soup.find("a", href=True)
            link = "https://www.flipkart.com" + link_tag["href"] if link_tag else None

            title_tag = soup.find("a", title=True)
            title = title_tag["title"] if title_tag else "N/A"

            price_tag = soup.find(string=lambda text: text and "₹" in text)
            price = price_tag.strip() if price_tag else "SOLD OUT"

            image_tag = link_tag.find("img") if link_tag else None
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
