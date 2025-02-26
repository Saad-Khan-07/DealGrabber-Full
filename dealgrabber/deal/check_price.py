from db import DatabaseHandler
from deal.price_handler import HandlePrice
from deal.mail_notification import DealNotiyMail

dbhandler = DatabaseHandler()

def check_price_deal():
    product_price_list = dbhandler.get_all_price_requests()

    for product in product_price_list:
        try:
            hp = HandlePrice(product[4], product[2], product[5])  # target_price, URL, shoesize
            db = hp.check_price()
            print(db)

            if int(db["current_price"]) <= int(product[4]):  # Compare correctly
                dm = DealNotiyMail(product[1], product[3], product[4], product[2])
                dm.send_deal_mail()
                print(f"✅ Deal email sent for {product[3]}")
            else:
                print("❌ No deal available, skipping...")

        except Exception as e:
            print(f"Error checking price: {e}")

check_price_deal()
