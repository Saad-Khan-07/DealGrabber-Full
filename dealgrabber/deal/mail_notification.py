import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL = "saaaadd53@gmail.com"
PWD = "ulfxecirdrwngcqt"

class SMTPClient:
    """Handles a persistent SMTP connection for reuse."""
    def __init__(self):
        self.server = smtplib.SMTP("smtp.gmail.com", 587)
        self.server.starttls()
        self.server.login(EMAIL, PWD)

    def send_email(self, receiver, subject, body):
        """Sends an email using the existing SMTP connection."""
        msg = MIMEMultipart()
        msg["From"] = f"DealGrabber <{EMAIL}>"
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            self.server.sendmail(EMAIL, receiver, msg.as_string())
            print(f"Email sent successfully to {receiver}!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def close(self):
        """Closes the SMTP connection."""
        self.server.quit()

# ✅ Now reuse the same connection for all email classes
class SendAvailabilityMail:
    def __init__(self, smtp_client, receiver, name, price, link):
        self.smtp_client = smtp_client
        self.receiver = receiver
        self.name = name
        self.price = price
        self.link = link

    def send_availability_mail(self):
        subject = "Your deal is now Available!!!"
        body = f"""
            Hello user,
            Check out the {self.name} before it goes Out of Stock again!!
            It's available on Flipkart now!!
            Price: {self.price}
            Link: {self.link}
        """
        self.smtp_client.send_email(self.receiver, subject, body)

class DealNotiyMail:
    def __init__(self, smtp_client, receiver, name, price, link):
        self.smtp_client = smtp_client
        self.receiver = receiver
        self.name = name
        self.price = price
        self.link = link

    def send_deal_mail(self):
        subject = "Your deal is now Available at a Cheaper Price!!!"
        body = f"""
            Hello user,
            Check out the {self.name} before it goes Out of Stock again!!
            It's available on Flipkart now at your requested price!!
            Price: {self.price}
            Link: {self.link}
        """
        self.smtp_client.send_email(self.receiver, subject, body)

class ConfirmationMail:
    def __init__(self, smtp_client, receiver):
        self.smtp_client = smtp_client
        self.receiver = receiver

    def send_confirmation(self):
        subject = "DealGrabber - Confirmation Mail"
        body = """
            Hello there, this mall is to inform you that your request to get notifications on deals is submitted.
            Thank you for considering DealGrabber!
        """
        self.smtp_client.send_email(self.receiver, subject, body)

# ✅ NEW CLASS - OTP Email
class OTPMail:
    def __init__(self, smtp_client, receiver, otp):
        self.smtp_client = smtp_client
        self.receiver = receiver
        self.otp = otp

    def send_otp_mail(self):
        subject = "DealGrabber - Email Verification Code"
        body = f"""
            Hello,
            
            You requested to view your DealGrabber notifications.
            
            Your verification code is: {self.otp}
            
            This code will expire in 10 minutes for security reasons.
            
            If you did not request this code, please ignore this email.
            
            Best regards,
            DealGrabber Team
        """
        self.smtp_client.send_email(self.receiver, subject, body)