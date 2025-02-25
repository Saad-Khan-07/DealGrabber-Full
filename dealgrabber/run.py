from deal.app import ProductInfo
from deal.avaliablility_handler import CheckAvailability
from deal.price_handler import HandlePrice
from deal.mail_notification import ConfirmationMail
from deal.db import DatabaseHandler
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import argparse
import sys
import json

def search_product(product_name=None):
    """
    Search for product and return product information
    If product_name is provided, use it instead of asking user
    """
    productinfo = ProductInfo()
    
    # Use provided product name if available, otherwise let ProductInfo ask
    if product_name:
        # Need to modify ProductInfo to accept product_name parameter
        # For now, we'll set it directly
        productinfo.productname = product_name
        productinfo.driver.get(f"https://www.flipkart.com/")
        searchinput = productinfo.driver.find_element(By.CSS_SELECTOR, 'input[title="Search for Products, Brands and More"]')
        searchinput.send_keys(product_name)
        searchinput.send_keys(Keys.RETURN)
        productinfo.driver.implicitly_wait(5)
    else:
        productinfo.search_product()
    
    info_dict = productinfo.get_product()
    productinfo.close_driver()
    print(json.dumps(info_dict))
    return info_dict

def check_availability(link, shoesize, email):
    """Check product availability and set up notification"""
    datahandler = DatabaseHandler()
    
    ca = CheckAvailability(link, shoesize)
    dataset = ca.check_availability()
    ca.close_driver()
    
    datahandler.store_availability_request(email, dataset["link"], dataset["name"], shoesize)
    cm = ConfirmationMail(email)
    cm.send_confirmation()
    print(f"Availability notification set up for {email}")
    
    print(json.dumps(dataset))
    return dataset

def check_price(link, shoesize, target_price, email):
    """Check product price and set up notification"""
    datahandler = DatabaseHandler()
    
    hp = HandlePrice(target_price, link, shoesize)
    dataset = hp.check_price()
    hp.closedriver()
    
    datahandler.store_price_request(email, link, dataset["name"], dataset["price"], shoesize)
    cm = ConfirmationMail(email)
    cm.send_confirmation()
    print(f"Price notification set up for {email}")
    
    print(json.dumps(dataset))
    return dataset

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="DealGrabber CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Search product command
    search_parser = subparsers.add_parser('search', help='Search for a product')
    search_parser.add_argument('--product_name', help='Product name to search for')
    
    # Availability command
    avail_parser = subparsers.add_parser('availability', help='Check product availability')
    avail_parser.add_argument('--link', required=True, help='Product URL')
    avail_parser.add_argument('--shoesize', required=True, help='Shoe size')
    avail_parser.add_argument('--email', required=True, help='Email for notification')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Check product price')
    price_parser.add_argument('--link', required=True, help='Product URL')
    price_parser.add_argument('--shoesize', required=True, help='Shoe size')
    price_parser.add_argument('--target_price', required=True, type=int, help='Target price threshold')
    price_parser.add_argument('--email', required=True, help='Email for notification')
    
    return parser.parse_args()

if __name__ == "__main__":
    # Interactive mode (original functionality)
    if len(sys.argv) == 1:
        datahandler = DatabaseHandler()
        productinfo = ProductInfo()
        productinfo.search_product()
        info_dict = productinfo.get_product()

        mail = input("Enter the mail you want to receive notifications on: ")
        choice = int(input("Enter: \n1. if you want to set up notifications for availability of the product \n2. if you want to set up notifications for a discount on your product"))

        if choice == 1:
            ca = CheckAvailability(info_dict["link"], info_dict["shoesize"])
            dataset = ca.check_availability()
            ca.close_driver()
            datahandler.store_availability_request(mail, dataset["link"], dataset["name"], info_dict["shoesize"])
            cm = ConfirmationMail(mail)
            cm.send_confirmation()
            print("Your request has been submitted! You'll Receive a confirmation Mail of the same.")
        if choice == 2:
            thprice = int(input("Enter the price(prices lower than this price will be notified): "))
            hp = HandlePrice(thprice, info_dict["link"], info_dict["shoesize"])
            dataset = hp.check_price()
            hp.closedriver()
            datahandler.store_price_request(mail, info_dict["link"], dataset["name"], dataset["price"], info_dict["shoesize"])
            cm = ConfirmationMail(mail)
            cm.send_confirmation()
            print("Your request has been submitted! You'll Receive a confirmation Mail of the same.")
    # Command line mode (for app.py integration)
    else:
        args = parse_arguments()
        
        if args.command == 'search':
            search_product(args.product_name)
        elif args.command == 'availability':
            check_availability(args.link, args.shoesize, args.email)
        elif args.command == 'price':
            check_price(args.link, args.shoesize, args.target_price, args.email)