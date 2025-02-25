from db import DatabaseHandler
from deal.price_handler import HandlePrice
from deal.mail_notification import DealNotiyMail

dbhandler= DatabaseHandler()

def check_price_deal():
    product_price_list= dbhandler.get_all_price_requests()
    for product in product_price_list:
        hp = HandlePrice(product[4],product[2], product[5])
        db = hp.check_price()
        print(db)
        if(int(db["current_price"])<=int(db["price"])):
            dm = DealNotiyMail(product[1],product[3], product[4], product[2])
            dm.send_deal_mail()
        else:
            print("didtn work")
            continue

check_price_deal()