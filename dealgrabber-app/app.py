import sys
import os
import random
import time
from datetime import datetime, timedelta

# Add the `DealGrabber` directory to Python's search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dealgrabber.deal.db import DatabaseHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from dealgrabber.run import search_product_run, check_availability, check_price
from dealgrabber.deal.mail_notification import SMTPClient, OTPMail  # Import the new OTP mail class

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")  # Use environment variable for security

# Initialize Database Pool
DatabaseHandler.initialize_pool()

# In-memory OTP storage (in production, consider using Redis or database)
# Structure: {email: {"otp": "123456", "timestamp": datetime_obj, "attempts": 0}}
otp_storage = {}

# OTP Configuration
OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3

def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def is_otp_valid(email, entered_otp):
    """Check if the entered OTP is valid for the given email"""
    if email not in otp_storage:
        return False, "No OTP found for this email"
    
    stored_data = otp_storage[email]
    
    # Check if OTP has expired
    if datetime.now() > stored_data["timestamp"] + timedelta(minutes=OTP_EXPIRY_MINUTES):
        del otp_storage[email]  # Clean up expired OTP
        return False, "OTP has expired. Please request a new one."
    
    # Check attempts limit
    if stored_data["attempts"] >= MAX_OTP_ATTEMPTS:
        del otp_storage[email]  # Clean up after max attempts
        return False, "Maximum OTP attempts exceeded. Please request a new one."
    
    # Check if OTP matches
    if stored_data["otp"] == entered_otp:
        del otp_storage[email]  # Clean up successful OTP
        return True, "OTP verified successfully"
    else:
        stored_data["attempts"] += 1
        return False, f"Invalid OTP. {MAX_OTP_ATTEMPTS - stored_data['attempts']} attempts remaining."

def send_otp_email(email):
    """Send OTP to the given email address"""
    try:
        otp = generate_otp()
        
        # Store OTP with timestamp
        otp_storage[email] = {
            "otp": otp,
            "timestamp": datetime.now(),
            "attempts": 0
        }
        
        # Send email using existing SMTP system
        smtp_client = SMTPClient()
        otp_mail = OTPMail(smtp_client, email, otp)
        otp_mail.send_otp_mail()
        smtp_client.close()
        
        return True, "OTP sent successfully"
    except Exception as e:
        return False, f"Failed to send OTP: {str(e)}"

@app.route("/")
def home():
    session.clear()  # Clear all session data on homepage visit
    return render_template("index.html")

@app.route("/search-product", methods=["GET", "POST"])
def search_product_route():
    session.clear()  # Clear old session data
    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        email = request.form.get("email", "").strip()
        session["email"] = email
        try:
            result_list = search_product_run(product_name)
            if result_list:
                session["result_list"] = result_list
                return render_template("select_product.html", result_list=result_list, email=email)

            return render_template("error.html", error="No valid product found. Please refine your search.")

        except Exception as e:
            return jsonify({"error": str(e)}), 500  

    return render_template("search_product.html")

@app.route("/select-link", methods=["GET"])
def select_link():
    selected_link = request.args.get("selected_link", "")
    if not selected_link:
        return redirect(url_for("search_product_route"))

    product_info = next((p for p in session.get("result_list", []) if p["link"] == selected_link), {})
    if not product_info:
        return render_template("error.html", error="Selected product not found. Try again.")

    session["product_info"] = product_info
    return render_template("product_info.html", product=product_info, email=session.get("email", ""))

@app.route("/select-product", methods=["GET"])
def select_product_route():
    result_list = session.get("result_list", [])

    # 🔥 If no search results exist, force user to search again
    if not result_list:
        return redirect(url_for("search_product_route"))

    return render_template("select_product.html", result_list=result_list, email=session.get("email", ""))

@app.route("/setup-notification", methods=["GET"])
def setup_notification():
    notification_type = request.args.get("type", "")
    if notification_type == "availability":
        return redirect(url_for("add_availability"))
    elif notification_type == "price":
        return redirect(url_for("add_price"))
    else:
        return redirect(url_for("home"))

@app.route("/add-availability", methods=["GET", "POST"])
def add_availability():
    db_handler = DatabaseHandler()
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]
        shoesize = request.form.get("shoesize", "0")

        if db_handler.check_availability_exists(email, product_link):
            return render_template("error.html", error="You already have an availability request for this product.")

        try:
            # Let check_availability handle the database operation
            dataset, success = check_availability(product_link, shoesize, email)
            
            if success:
                return render_template("confirmation.html", message="Your availability notification has been set up!")
            return render_template("error.html", error="Failed to set up notification.")
        except Exception as e:
            return render_template("error.html", error=str(e))

    product_info = session.get("product_info", {})
    email = session.get("email", "")
    return render_template("add_availability.html", product_link=product_info.get("link", ""), shoesize=product_info.get("shoesize", ""), email=email)

@app.route("/add-price", methods=["GET", "POST"])
def add_price():
    db_handler = DatabaseHandler()
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]
        target_price = request.form["target_price"]
        shoesize = request.form.get("shoesize", "0")

        if db_handler.check_price_exists(email, product_link):
            return render_template("error.html", error="You already have a price request for this product.")
        try:
            # Let check_price handle the database operation
            dataset = check_price(product_link, shoesize, target_price, email)
            
            # If we got here without exceptions, assume it worked
            return render_template("confirmation.html", message="Your price notification has been set up!")
        except Exception as e:
            return render_template("error.html", error=str(e))

    product_info = session.get("product_info", {})
    email = session.get("email", "")
    return render_template("add_price.html", product_link=product_info.get("link", ""), shoesize=product_info.get("shoesize", ""), email=email)

# ✅ UPDATED DELETE PRODUCT ROUTE - Now sends OTP instead of showing products directly

@app.route("/delete-product", methods=["GET", "POST"])
def delete_product():
    """Entry point - Email collection only"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return render_template("delete_product.html", error="Please enter your email.")

        # Check if user has any notifications before sending OTP
        db_handler = DatabaseHandler()
        availability_notifications = db_handler.get_availability_notifications(email)
        price_notifications = db_handler.get_price_notifications(email)

        if not availability_notifications and not price_notifications:
            return render_template("delete_product.html", error="No notifications found for this email.")

        # Send OTP to email
        success, message = send_otp_email(email)
        print(f"OTP send result: {success}, Message: {message}")  # DEBUG
        
        if success:
            session["pending_email"] = email
            return redirect(url_for("verify_otp"))
        else:
            return render_template("delete_product.html", error=f"Failed to send OTP: {message}")

    # GET request - show email entry form only
    return render_template("delete_product.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    """OTP verification page"""
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("delete_product"))

    if request.method == "POST":
        entered_otp = request.form.get("otp", "").strip()
        if not entered_otp:
            return render_template("verify_otp.html", email=email, error="Please enter the OTP.")

        # Verify OTP
        is_valid, message = is_otp_valid(email, entered_otp)
        print(f"OTP validation result: {is_valid}, Message: {message}")  # DEBUG
        
        if is_valid:
            # OTP is correct, redirect to delete list page
            session.pop("pending_email", None)
            session["verified_email"] = email  # Store verified email
            return redirect(url_for("delete_list"))
        else:
            return render_template("verify_otp.html", email=email, error=message)

    return render_template("verify_otp.html", email=email)

@app.route("/delete-list")
def delete_list():
    """Show notifications list for verified email"""
    email = session.get("verified_email")
    if not email:
        return redirect(url_for("delete_product"))

    # Fetch notifications for the verified email
    db_handler = DatabaseHandler()
    availability_notifications = db_handler.get_availability_notifications(email)
    price_notifications = db_handler.get_price_notifications(email)

    # Check if any notifications exist
    if not availability_notifications and not price_notifications:
        return render_template("delete_list.html", 
                             email=email, 
                             no_notifications=True)

    return render_template("delete_list.html", 
                         email=email,
                         availability_notifications=availability_notifications,
                         price_notifications=price_notifications)

@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Resend OTP"""
    email = session.get("pending_email")
    if not email:
        return redirect(url_for("delete_product"))

    success, message = send_otp_email(email)
    if success:
        return render_template("verify_otp.html", email=email, success="New OTP sent to your email!")
    else:
        return render_template("verify_otp.html", email=email, error=f"Failed to resend OTP: {message}")

@app.route("/confirm-delete-notification", methods=["POST"])
def confirm_delete_notification():
    """Handle individual notification deletion"""
    # Check if user has verified email in session
    email = session.get("verified_email")
    if not email:
        return redirect(url_for("delete_product"))

    notification_id = request.form.get("notification_id", "").strip()
    notification_type = request.form.get("notification_type", "").strip()

    if not notification_id or not notification_type:
        return redirect(url_for("delete_list"))

    # Delete the notification
    db_handler = DatabaseHandler()
    success = db_handler.delete_request(notification_id, email, notification_type)

    # Clear verified email from session after deletion
    session.pop("verified_email", None)

    if success:
        return render_template("delete_confirmation.html", 
                             success=True, 
                             message="Notification deleted successfully!",
                             email=email)
    else:
        return render_template("delete_confirmation.html", 
                             success=False, 
                             message="Failed to delete notification. Please try again.",
                             email=email)

# Fixed OTP functions
def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def is_otp_valid(email, entered_otp):
    """Check if the entered OTP is valid for the given email"""
    if email not in otp_storage:
        return False, "No OTP found for this email"
    
    stored_data = otp_storage[email]
    
    # Check if OTP has expired
    if datetime.now() > stored_data["timestamp"] + timedelta(minutes=OTP_EXPIRY_MINUTES):
        del otp_storage[email]  # Clean up expired OTP
        return False, "OTP has expired. Please request a new one."
    
    # Check attempts limit
    if stored_data["attempts"] >= MAX_OTP_ATTEMPTS:
        del otp_storage[email]  # Clean up after max attempts
        return False, "Maximum OTP attempts exceeded. Please request a new one."
    
    # Check if OTP matches
    if stored_data["otp"] == entered_otp:
        del otp_storage[email]  # Clean up successful OTP
        return True, "OTP verified successfully"
    else:
        stored_data["attempts"] += 1
        return False, f"Invalid OTP. {MAX_OTP_ATTEMPTS - stored_data['attempts']} attempts remaining."

def send_otp_email(email):
    """Send OTP to the given email address"""
    try:
        otp = generate_otp()
        
        # Store OTP with timestamp
        otp_storage[email] = {
            "otp": otp,
            "timestamp": datetime.now(),
            "attempts": 0
        }
        
        print(f"Generated OTP for {email}: {otp}")  # DEBUG - Remove in production
        
        # Send email using existing SMTP system
        smtp_client = SMTPClient()
        otp_mail = OTPMail(smtp_client, email, otp)
        otp_mail.send_otp_mail()
        smtp_client.close()
        
        print(f"OTP email sent successfully to {email}")  # DEBUG
        return True, "OTP sent successfully"
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")  # DEBUG
        return False, f"Failed to send OTP: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))