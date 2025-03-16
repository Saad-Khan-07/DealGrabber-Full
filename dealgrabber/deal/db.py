import psycopg2

DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"

def get_db_connection():
    """Creates a new database connection for each request."""
    return psycopg2.connect(DATABASE_URL)

class DatabaseHandler:
    def check_availability_exists(self, email, product_link):
        """Checks if an availability request already exists for the given email and product link."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS(SELECT 1 FROM availability_requests WHERE email = %s AND product_link = %s)
        """, (email, product_link))
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists

    def check_price_exists(self, email, product_link):
        """Checks if a price request already exists for the given email and product link."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT EXISTS(SELECT 1 FROM price_requests WHERE email = %s AND product_link = %s)
        """, (email, product_link))
        exists = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return exists
    
    def store_availability_request(self, email, product_link, name, shoesize):
        """Inserts an availability request into the database if it doesn't exist."""
        try:
            # First check if this request already exists
            if self.check_availability_exists(email, product_link):
                return False, "An availability request for this product already exists."
                
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO availability_requests (email, product_link, product_name, shoesize)
                VALUES (%s, %s, %s, %s)
            """, (email, product_link, name, shoesize))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Success"
        except psycopg2.Error as e:
            print(f"Database Error (store_availability_request): {e}")
            return False, str(e)

    def store_price_request(self, email, product_link, name, target_price, shoesize):
        """Inserts a price request into the database if it doesn't exist."""
        try:
            # First check if this request already exists
            if self.check_price_exists(email, product_link):
                return False, "A price request for this product already exists."
                
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_requests (email, product_link, product_name, target_price, shoesize)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, product_link, name, target_price, shoesize))
            conn.commit()
            cursor.close()
            conn.close()
            return True, "Success"
        except psycopg2.Error as e:
            print(f"Database Error (store_price_request): {e}")
            return False, str(e)

    def get_all_availability_requests(self):
        """Fetches all records from the availability_requests table."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM availability_requests")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except psycopg2.Error as e:
            print(f"Database Error (get_all_availability_requests): {e}")
            return []

    def get_all_price_requests(self):
        """Fetches all records from the price_requests table."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM price_requests")
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except psycopg2.Error as e:
            print(f"Database Error (get_all_price_requests): {e}")
            return []

    def get_availability_notifications(self, email):
        """Fetches all availability notifications for a given email."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, product_link FROM availability_requests WHERE email = %s", (email,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def get_price_notifications(self, email):
        """Fetches all price notifications for a given email."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_name, product_link, target_price FROM price_requests WHERE email = %s", (email,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results

    def delete_request(self, notification_id, email, notification_type):
        """Deletes a notification from the database by ID and email."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if notification_type == "availability":
            cursor.execute("DELETE FROM availability_requests WHERE id = %s AND email = %s", (notification_id, email))
        elif notification_type == "price":
            cursor.execute("DELETE FROM price_requests WHERE id = %s AND email = %s", (notification_id, email))

        conn.commit()
        cursor.close()
        conn.close()
