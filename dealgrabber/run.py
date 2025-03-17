from dealgrabber.deal.app import ProductInfo
from dealgrabber.deal.avaliablility_handler import CheckAvailability
from dealgrabber.deal.price_handler import HandlePrice
from dealgrabber.deal.mail_notification import SMTPClient, ConfirmationMail
from dealgrabber.deal.db import DatabaseHandler
import argparse
import json

def search_product_run(product_name=None):
    """Search for product and return product information"""
    productinfo = ProductInfo()
    productinfo.search_product(product_name)
    top_results_list = productinfo.get_product()
    productinfo.close_driver()
    
    print(json.dumps(top_results_list))
    return top_results_list

def check_availability(link, shoesize, email):
    """Check product availability and set up notification"""
    ca = CheckAvailability(link, shoesize)
    dataset = ca.check_availability()
    ca.close_driver()

    smtp_client = SMTPClient()
    
    try:
        success, message = DatabaseHandler().store_availability_request(email, dataset["link"], dataset["name"], shoesize)
        if not success:
            return {"error": message}

        ConfirmationMail(smtp_client, email).send_confirmation()
        print(f"Availability notification set up for {email}")
    finally:
        smtp_client.close()

    print(json.dumps(dataset))
    return dataset

def check_price(link, shoesize, target_price, email):
    """Check product price and set up notification"""
    hp = HandlePrice(target_price, link, shoesize)
    dataset = hp.check_price()
    hp.close_driver()

    smtp_client = SMTPClient()
    
    try:
        success, message = DatabaseHandler().store_price_request(email, link, dataset["name"], dataset["price"], shoesize)
        if not success:
            return {"error": message}

        ConfirmationMail(smtp_client, email).send_confirmation()
        print(f"Price notification set up for {email}")
    finally:
        smtp_client.close()

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
