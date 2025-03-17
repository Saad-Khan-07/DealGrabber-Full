import sys
import os
# Add the `DealGrabber` directory to Python's search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dealgrabber.deal.db import DatabaseHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import psycopg2
from dealgrabber.run import search_product_run, check_availability, check_price  # ✅ Make sure this function exists in `run.py`

app = Flask(__name__)
app.secret_key = "ulfxecirdrwngcqt"  # Needed for session

# PostgreSQL Connection
DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    session.pop("result_list", None)   # Remove previous search results
    session.pop("product_info", None)  # Remove previously selected product
    session.pop("email", None)  # Remove previously selected product
    return render_template("index.html")  # Homepage

@app.route("/search-product", methods=["GET", "POST"])
def search_product_route():
    session.pop("result_list", None)   # Remove previous search results
    session.pop("product_info", None)  # Remove previously selected product
    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        email = request.form.get("email", "").strip()

        # Store email in session for later use
        session["email"] = email

        try:
            # ✅ Get the list of top 5 results
            result_list = search_product_run(product_name)

            if result_list:
                # ✅ Store the result list in session so it can be used later
                session["result_list"] = result_list
                return render_template("select_product.html", result_list=result_list, email=email)

            # 🔴 If no results found, show error message
            return render_template("error.html", error="No valid product found. Please refine your search.")

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Only one return statement

    return render_template("search_product.html")  # Renders search form

@app.route("/select-link", methods=["GET", "POST"])
def select_link():
    selected_link = request.args.get("selected_link", "")  # ✅ Change to GET

    if not selected_link:
        return redirect(url_for("search_product_route"))  # Redirect if no link selected

    # ✅ Find the selected product from the stored result list
    product_info = next((p for p in session.get('result_list', []) if p["link"] == selected_link), {})

    if not product_info:
        return render_template("error.html", error="Selected product not found. Try again.")

    # ✅ Store selected product in session
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

# 📌 Route for adding a product for availability notification

@app.route("/add-availability", methods=["GET", "POST"])
def add_availability():
    db_handler = DatabaseHandler()
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]
        shoesize = request.form.get("shoesize", "0")

        if db_handler.check_availability_exists(email, product_link):
            return render_template("error.html", error="You already have an availability request for this product.")

        dataset = check_availability(product_link, shoesize, email)
        success, message = db_handler.store_availability_request(email, product_link, dataset.get("name", ""), shoesize)

        if success:
            return render_template("confirmation.html", message="Your availability notification has been set up!")
        return render_template("error.html", error=message)

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

        dataset = check_price(product_link, shoesize, target_price, email)
        success, message = db_handler.store_price_request(email, product_link, dataset.get("name", ""), target_price, shoesize)

        if success:
            return render_template("confirmation.html", message="Your price notification has been set up!")
        return render_template("error.html", error=message)

    product_info = session.get("product_info", {})
    email = session.get("email", "")
    return render_template("add_price.html", product_link=product_info.get("link", ""), shoesize=product_info.get("shoesize", ""), email=email)

# 📌 Route for deleting a product notification
@app.route("/delete-product", methods=["GET", "POST"])
def delete_product():
    db_handler = DatabaseHandler()
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            return render_template("delete_product.html", error="Please enter your email.")

        availability_notifications = db_handler.get_availability_notifications(email)
        price_notifications = db_handler.get_price_notifications(email)

        if not availability_notifications and not price_notifications:
            return render_template("delete_product.html", error="No notifications found for this email.")

        return render_template("delete_product.html", email=email, availability_notifications=availability_notifications, price_notifications=price_notifications)

    return render_template("delete_product.html")

@app.route("/confirm-delete-notification", methods=["POST"])
def confirm_delete_notification():
    db_handler = DatabaseHandler()
    email = request.form.get("email", "").strip()
    notification_id = request.form.get("notification_id", "").strip()
    notification_type = request.form.get("notification_type", "").strip()

    if not email or not notification_id:
        return redirect(url_for("delete_product", error="Invalid request."))

    success = db_handler.delete_request(notification_id, email, notification_type)

    if success:
        return redirect(url_for("delete_product", email=email, success="Notification deleted successfully."))
    return redirect(url_for("delete_product", email=email, error="Failed to delete notification."))

if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))