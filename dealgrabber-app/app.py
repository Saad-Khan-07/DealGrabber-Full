import sys
import os
# Add the `DealGrabber` directory to Python's search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dealgrabber.deal.db import DatabaseHandler
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import psycopg2
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dealgrabber.deal.app import ProductInfo
from dealgrabber.run import search_product_run, check_availability, check_price  # ✅ Make sure this function exists in `run.py`

app = Flask(__name__)
app.secret_key = "ulfxecirdrwngcqt"  # Needed for session

# PostgreSQL Connection
DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return render_template("index.html")  # Homepage


@app.route("/search-product", methods=["GET", "POST"])
def search_product_route():  # Renamed to avoid recursion error
    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        email = request.form.get("email", "").strip()

        # Store email in session for later use
        session["email"] = email

        try:
            # ✅ Call the function directly instead of subprocess
            info_dict = search_product_run(product_name)  

            # ✅ Always return a **single** link
            if "link" in info_dict:
                session["product_info"] = info_dict
                return render_template("product_info.html", product=info_dict, email=email)
            
            # 🔴 If no link is found, instruct the user to refine the search
            return render_template("error.html", error="No valid product link found. Please refine your search.")

        except Exception as e:
            return jsonify({"error": str(e)}), 500  # Only one return statement

    return render_template("search_product.html")  # Renders search form

@app.route("/select-link", methods=["POST"])
def select_link():
    selected_link = request.form.get("selected_link", "")
    custom_link = request.form.get("custom_link", "")
    
    link = custom_link if custom_link else selected_link
    shoesize = session.get('shoesize', 0)
    email = session.get('email', '')
    
    product_info = {
        "link": link,
        "shoesize": shoesize
    }
    
    session['product_info'] = product_info
    
    return render_template("product_info.html", product=product_info, email=email)

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
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]
        shoesize = request.form.get("shoesize", "0")  # Optional field

        try:
            # ✅ Call `check_availability` directly instead of using subprocess
            dataset = check_availability(product_link, shoesize, email)

            # Store in PostgreSQL database as well
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO availability_requests (email, product_link, product_name, shoesize)
                VALUES (%s, %s, %s, %s)
            """, (email, product_link, dataset.get("name", ""), shoesize))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template("confirmation.html", message="Your availability notification has been set up!")
        except Exception as e:
            return render_template("error.html", error=str(e))

    # GET request - prepopulate form with session data
    product_info = session.get("product_info", {})
    email = session.get("email", "")

    return render_template(
        "add_availability.html",
        product_link=product_info.get("link", ""),
        shoesize=product_info.get("shoesize", ""),
        email=email,
    )

# 📌 Route for adding a product for price notification
@app.route("/add-price", methods=["GET", "POST"])
def add_price():
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]
        target_price = request.form["target_price"]
        shoesize = request.form.get("shoesize", "0")  # Optional field

        try:
            # ✅ Call `check_price` directly instead of using subprocess
            dataset = check_price(product_link, shoesize, target_price, email)

            # Store in PostgreSQL database as well
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_requests (email, product_link, product_name, target_price, shoesize)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, product_link, dataset.get("name", ""), target_price, shoesize))
            conn.commit()
            cursor.close()
            conn.close()

            return render_template("confirmation.html", message="Your price notification has been set up!")
        except Exception as e:
            return render_template("error.html", error=str(e))

    # GET request - prepopulate form with session data
    product_info = session.get("product_info", {})
    email = session.get("email", "")

    return render_template(
        "add_price.html",
        product_link=product_info.get("link", ""),
        shoesize=product_info.get("shoesize", ""),
        email=email,
    )
# 📌 Route for deleting a product notification
@app.route("/delete-product", methods=["GET", "POST"])
def delete_product():
    if request.method == "POST":
        email = request.form["email"]
        product_link = request.form["product_link"]

        try:
            db_handler = DatabaseHandler()  # ✅ Initialize Database Handler
            db_handler.delete_request(email, product_link)  # ✅ Call delete function

            return render_template("confirmation.html", message="Your product notification has been removed.")
        except Exception as e:
            return render_template("error.html", error=str(e))

    return render_template("delete_product.html")  # Renders delete request page

if __name__ == "__main__":
    app.run(debug=True)