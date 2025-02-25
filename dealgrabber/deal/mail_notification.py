import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from deal.avaliablility_handler import CheckAvailability
from deal.price_handler import HandlePrice

email= "saaaadd53@gmail.com"
pwd = "ulfxecirdrwngcqt"

class SendAvailabilityMail:
    def __init__(self, receiver, name, price, link):
        self.receiver= receiver
        self.name= name
        self.price= price
        self.link= link
        self.server= smtplib.SMTP("smtp.gmail.com", 587)
    
    def send_availability_mail(self):
        subject= "Your deal is now Available!!!"
        body = f"""
            Hello user,
            Check out the {self.name} before it goes Out of Stock again!!
            Its available on Flipkart now!!
            Price: {self.price}
            Link: {self.link}
        """
        msg= MIMEMultipart()
        msg["From"] = f"DealGrabber <{email}>"
        msg["To"]= f"{self.receiver}"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, pwd)
            server.sendmail(email, self.receiver, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")

class DealNotiyMail:
    def __init__(self, receiver, name, price, link):
        self.receiver= receiver
        self.name= name
        self.price= price
        self.link= link
        self.server= smtplib.SMTP("smtp.gmail.com", 587)
        
    def send_deal_mail(self):
        subject= "Your deal is now Available at a Cheaper Price!!!"
        body = f"""
            Hello user,
            Check out the {self.name} before it goes Out of Stock again!!
            Its available on Flipkart now at your requested price!!
            Price: {self.price}
            Link: {self.link}
        """
        msg= MIMEMultipart()
        msg["From"] = f"DealGrabber <{email}>"
        msg["To"]= f"{self.receiver}"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, pwd)
            server.sendmail(email, self.receiver, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")

class ConfirmationMail:
    def __init__(self, receiver):
        self.server= smtplib.SMTP("smtp.gmail.com", 587)
        self.receiver= receiver
    
    def send_confirmation(self):
        subject = "DealGrabber, Confirmation Mail"
        body = """
            Hello there, this mail is to inform you that your request to get notifications on deals is sumitted.
            Thank you for considering DealGrabber
"""
        msg= MIMEMultipart()
        msg["From"] = f"DealGrabber <{email}>"
        msg["To"]= f"{self.receiver}"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(email, pwd)
            server.sendmail(email, self.receiver, msg.as_string())
            server.quit()
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error: {e}")



# shoes = {"shoesize": 9,"shoes": True}
# link="https://www.flipkart.com/puma-rungryp-sneakers-men/p/itm7b4744135bc9c?pid=SHOGQAZD7MVX94YU&lid=LSTSHOGQAZD7MVX94YURTWUXM&marketplace=FLIPKART&q=puma+shoes&store=osp&srno=s_1_3&otracker=search&otracker1=search&fm=Search&iid=f2d678a8-fab2-47a9-adfc-860f6007712b.SHOGQAZD7MVX94YU.SEARCH&ppt=sp&ppn=sp&ssid=fx5xfr2k2o0000001740292012231&qH=12daa41359850f83"
# name= "FULL FORCE LO Sneakers For Men"
# price= "₹8,495"

# cm = ConfirmationMail("stupefyingbuttons@gmail.com")
# cm.send_confirmation()