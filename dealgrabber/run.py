from dealgrabber.deal.app import ProductInfo
from dealgrabber.deal.avaliablility_handler import CheckAvailability
from dealgrabber.deal.price_handler import HandlePrice
from dealgrabber.deal.mail_notification import SMTPClient, ConfirmationMail
from dealgrabber.deal.db import DatabaseHandler
import argparse
import concurrent.futures

def search_product_run(product_name=None):
    """Search for product and return product information (Optimized with ThreadPool)."""
    productinfo = ProductInfo()
    productinfo.search_product(product_name)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future = executor.submit(productinfo.get_product)  # No arguments
        top_results_list = future.result()

    
    productinfo.close_driver()
    return top_results_list

def check_availability(link, shoesize, email):
    """Check product availability and set up notification (Optimized with ThreadPool)."""
    db_handler = DatabaseHandler()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        exists_future = executor.submit(db_handler.check_availability_exists, email, link)
        exists = exists_future.result()

        if exists:
            return {"error": "An availability request for this product already exists."}

        ca = CheckAvailability(link, shoesize)
        dataset = ca.check_availability()
        ca.close_driver()

        if not dataset:
            return {"error": "Failed to retrieve product data"}

        smtp_client = SMTPClient()
        
        db_future = executor.submit(db_handler.store_availability_request, email, dataset["link"], dataset["name"], shoesize)
        email_future = executor.submit(ConfirmationMail(smtp_client, email).send_confirmation)

        success, message = db_future.result()
        email_future.result()
        smtp_client.close()

        if not success:
            return {"error": message}

    return dataset, success

def check_price(link, shoesize, target_price, email):
    """Check product price and set up notification (Optimized with ThreadPool)."""
    db_handler = DatabaseHandler()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        exists_future = executor.submit(db_handler.check_price_exists, email, link)
        exists = exists_future.result()

        if exists:
            return {"error": "A price request for this product already exists."}

        hp = HandlePrice(target_price, link, shoesize)
        dataset = hp.check_price()
        hp.close_driver()

        if not dataset or dataset.get("name") == "Unknown":
            return {"error": "Failed to retrieve product data"}

        smtp_client = SMTPClient()

        db_future = executor.submit(db_handler.store_price_request, email, link, dataset["name"], dataset["price"], shoesize)
        email_future = executor.submit(ConfirmationMail(smtp_client, email).send_confirmation)

        success, message = db_future.result()
        email_future.result()
        smtp_client.close()

        if not success:
            return {"error": message}

    return dataset

def batch_process_notifications(batch_size=10):
    """Process multiple notifications in parallel (Now with grouped batching)."""
    db_handler = DatabaseHandler()
    availability_requests, price_requests = db_handler.batch_get_requests(batch_size)

    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        availability_futures = [executor.submit(process_availability_request, req) for req in availability_requests]
        price_futures = [executor.submit(process_price_request, req) for req in price_requests]

        for future in concurrent.futures.as_completed(availability_futures + price_futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})

    return results

def process_availability_request(request):
    """Process a single availability request."""
    id, email, link, name, shoesize = request
    ca = CheckAvailability(link, shoesize)
    result = ca.check_availability()
    ca.close_driver()

    return {"id": id, "type": "availability", "email": email, "product": name, "result": result}

def process_price_request(request):
    """Process a single price request."""
    id, email, link, name, target_price, shoesize = request
    hp = HandlePrice(target_price, link, shoesize)
    result = hp.check_price()
    hp.close_driver()

    return {"id": id, "type": "price", "email": email, "product": name, "result": result}

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DealGrabber CLI")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    search_parser = subparsers.add_parser('search', help='Search for a product')
    search_parser.add_argument('--product_name', help='Product name to search for')

    avail_parser = subparsers.add_parser('availability', help='Check product availability')
    avail_parser.add_argument('--link', required=True, help='Product URL')
    avail_parser.add_argument('--shoesize', required=True, help='Shoe size')
    avail_parser.add_argument('--email', required=True, help='Email for notification')

    price_parser = subparsers.add_parser('price', help='Check product price')
    price_parser.add_argument('--link', required=True, help='Product URL')
    price_parser.add_argument('--shoesize', required=True, help='Shoe size')
    price_parser.add_argument('--target_price', required=True, type=int, help='Target price threshold')
    price_parser.add_argument('--email', required=True, help='Email for notification')

    batch_parser = subparsers.add_parser('batch', help='Process notifications in batch')
    batch_parser.add_argument('--batch_size', type=int, default=10, help='Number of requests to process in batch')

    return parser.parse_args()
