from db import DatabaseHandler
from deal.avaliablility_handler import CheckAvailability
from deal.mail_notification import SendAvailabilityMail

dbhandler= DatabaseHandler()

def check_price_deal():
    product_price_list= dbhandler.get_all_price_requests()
    for product in product_price_list:
        ca = CheckAvailability(product[2],product[4])
        db = ca.check_availability()
        print(db)
        if(db["availability"]):
            dm = SendAvailabilityMail(product[1], product[3], db["price"], product[2])
            dm.send_availability_mail()
        else:
            print("didtn work")
            continue

check_price_deal()