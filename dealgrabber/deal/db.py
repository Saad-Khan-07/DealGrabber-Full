import psycopg2

DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"

def get_db_connection():
    """Creates a new database connection for each request."""
    return psycopg2.connect(DATABASE_URL)

class DatabaseHandler:
    def store_availability_request(self, email, product_link, name, shoesize):
        """Inserts an availability request into the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO availability_requests (email, product_link, product_name, shoesize)
                VALUES (%s, %s, %s, %s)
            """, (email, product_link, name, shoesize))
            conn.commit()
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database Error (store_availability_request): {e}")

    def store_price_request(self, email, product_link, name, target_price, shoesize):
        """Inserts a price request into the database."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_requests (email, product_link, product_name, target_price, shoesize)
                VALUES (%s, %s, %s, %s, %s)
            """, (email, product_link, name, target_price, shoesize))
            conn.commit()
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Database Error (store_price_request): {e}")

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
