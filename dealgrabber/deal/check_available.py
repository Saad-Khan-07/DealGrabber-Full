from db import DatabaseHandler
from dealgrabber.deal.avaliablility_handler import CheckAvailability
from dealgrabber.deal.mail_notification import SendAvailabilityMail

dbhandler = DatabaseHandler()

def check_availability_deal():
    product_availability_list = dbhandler.get_all_availability_requests()
    
    for product in product_availability_list:
        try:
            ca = CheckAvailability(product[2], product[4])  # URL and shoesize
            db = ca.check_availability()
            print(db)

            if db.get("availability", False):
                dm = SendAvailabilityMail(product[1], product[3], db["price"], product[2])
                dm.send_availability_mail()
            else:
                continue
        
        except Exception as e:
            print(f"Error checking availability: {e}")

check_availability_deal()