from dealgrabber.deal.db import DatabaseHandler
from dealgrabber.deal.price_handler import HandlePrice
from dealgrabber.deal.mail_notification import DealNotiyMail
from dealgrabber.deal.mail_notification import SMTPClient

dbhandler = DatabaseHandler()

def check_price_deal():
    product_price_list = dbhandler.get_all_price_requests()
    smtp_client = SMTPClient()
    for product in product_price_list:
        try:
            hp = HandlePrice(product[4], product[2], product[5])  # target_price, URL, shoesize
            db = hp.check_price()
            print(db)

            if int(db["current_price"]) <= int(product[4]):  # Compare correctly
                dm = DealNotiyMail(smtp_client=smtp_client, receiver=product[1], name=product[3], price=int(db["current_price"]), link=product[2])
                dm.send_deal_mail()
            else:
                continue

        except Exception as e:
            print(f"Error checking price: {e}")

check_price_deal()