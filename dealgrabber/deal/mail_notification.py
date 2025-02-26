import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ✅ Configure logging for cloud logging
logging.basicConfig(filename='logs.log', encoding='utf-8', level=logging.DEBUG, 
format='%(asctime)s - %(levelname)s - %(message)s')

# ✅ Use Environment Variables Instead of Hardcoded Credentials
EMAIL_USER = os.getenv("EMAIL_USER")  # Set this in Railway's Environment Variables
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Set this in Railway's Environment Variables

class EmailSender:
    def __init__(self, receiver, subject, body):
        self.receiver = receiver
        self.subject = subject
        self.body = body

    def send_mail(self):
        """Send an email using Gmail SMTP."""
        msg = MIMEMultipart()
        msg["From"] = f"DealGrabber <{EMAIL_USER}>"
        msg["To"] = self.receiver
        msg["Subject"] = self.subject
        msg.attach(MIMEText(self.body, "plain"))

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, self.receiver, msg.as_string())
            server.quit()
            logging.info(f"✅ Email sent successfully to {self.receiver}")
        except Exception as e:
            logging.error(f"🚨 Email sending failed: {e}")

# ✅ Availability Email Notification
class SendAvailabilityMail(EmailSender):
    def __init__(self, receiver, name, price, link):
        subject = "Your deal is now Available!!!"
        body = f"""
        Hello,
        
        Check out the {name} before it goes out of stock again!
        Available now on Flipkart.
        Price: {price}
        
        👉 [Click Here]({link})
        """
        super().__init__(receiver, subject, body)

# ✅ Price Drop Email Notification
class DealNotifyMail(EmailSender):
    def __init__(self, receiver, name, price, link):
        subject = "Price Drop Alert! Your Deal is Available at a Lower Price!"
        body = f"""
        Hello,
        
        Check out the {name} before it goes out of stock again!
        Now available at your requested price on Flipkart.
        Price: {price}
        
        👉 [Click Here]({link})
        """
        super().__init__(receiver, subject, body)

# ✅ Confirmation Email
class ConfirmationMail(EmailSender):
    def __init__(self, receiver):
        subject = "DealGrabber: Confirmation Mail"
        body = """
        Hello,

        Your request to receive notifications about deals has been successfully submitted.
        Thank you for using DealGrabber!
        """
        super().__init__(receiver, subject, body)

# ✅ Example Usage:
if __name__ == "__main__":
    email = "test@example.com"
    
    # Send confirmation mail
    ConfirmationMail(email).send_mail()
    
    # Send availability alert
    SendAvailabilityMail(email, "Nike Sneakers", "₹5,499", "https://example.com/product").send_mail()
    
    # Send price drop alert
    DealNotifyMail(email, "Nike Sneakers", "₹4,999", "https://example.com/product").send_mail()
