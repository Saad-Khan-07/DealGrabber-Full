import os
from dealgrabber.deal.db import DatabaseHandler
from dealgrabber.deal.avaliablility_handler import CheckAvailability
from dealgrabber.deal.mail_notification import SendAvailabilityMail
from dealgrabber.deal.mail_notification import SMTPClient


dbhandler = DatabaseHandler()

def check_availability_deal():
    # --- STEP 1: Instantiate the SMTP client once, outside the loop ---
    # This assumes your SMTPClient class is now reading from environment variables
    # smtp_client = SMTPClient(os.getenv("EMAIL"), os.getenv("PWD"))
    # Or, if your SMTPClient class is hardcoded like your example:
    smtp_client = SMTPClient()

    product_availability_list = dbhandler.get_all_availability_requests()
    
    try:
        for product in product_availability_list:
            try:
                # Assuming product[2] is the link and product[4] is the shoesize
                ca = CheckAvailability(product[2], product[4])
                db = ca.check_availability()
                print(db)

                if db.get("availability", False):
                    # ✅ Pass the smtp_client instance and the correct arguments
                    dm = SendAvailabilityMail(
                        smtp_client=smtp_client,
                        receiver=product[1],
                        name=db.get("name"),
                        price=db.get("price"),
                        link=db.get("link")
                    )
                    dm.send_availability_mail()
                else:
                    continue
            
            except Exception as e:
                print(f"Error checking availability for product {product[0]}: {e}")
    finally:
        # ✅ Always make sure the connection is closed
        smtp_client.close()

check_availability_deal()