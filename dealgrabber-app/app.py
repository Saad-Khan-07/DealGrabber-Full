import psycopg2
from psycopg2 import pool
import contextlib

# Database connection parameters
DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"

# Create a connection pool with min and max connections
connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    dsn=DATABASE_URL
)

@contextlib.contextmanager
def get_db_connection():
    """Get a database connection from the pool using context manager for automatic cleanup."""
    conn = None
    try:
        conn = connection_pool.getconn()
        yield conn
    finally:
        if conn:
            connection_pool.putconn(conn)

@contextlib.contextmanager
def get_cursor(commit=False):
    """Get a cursor using the connection from the pool."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()

class DatabaseHandler:
    def check_availability_exists(self, email, product_link):
        """Checks if an availability request already exists for the given email and product link."""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM availability_requests WHERE email = %s AND product_link = %s)
            """, (email, product_link))
            return cursor.fetchone()[0]

    def check_price_exists(self, email, product_link):
        """Checks if a price request already exists for the given email and product link."""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM price_requests WHERE email = %s AND product_link = %s)
            """, (email, product_link))
            return cursor.fetchone()[0]
    
    def store_availability_request(self, email, product_link, name, shoesize):
        """Inserts an availability request into the database if it doesn't exist."""
        try:
            # First check if this request already exists
            if self.check_availability_exists(email, product_link):
                return False, "An availability request for this product already exists."
                
            with get_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO availability_requests (email, product_link, product_name, shoesize)
                    VALUES (%s, %s, %s, %s)
                """, (email, product_link, name, shoesize))
                
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
                
            with get_cursor(commit=True) as cursor:
                cursor.execute("""
                    INSERT INTO price_requests (email, product_link, product_name, target_price, shoesize)
                    VALUES (%s, %s, %s, %s, %s)
                """, (email, product_link, name, target_price, shoesize))
                
            return True, "Success"
        except psycopg2.Error as e:
            print(f"Database Error (store_price_request): {e}")
            return False, str(e)

    def get_all_availability_requests(self):
        """Fetches all records from the availability_requests table."""
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM availability_requests
                    ORDER BY id
                """)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Database Error (get_all_availability_requests): {e}")
            return []

    def get_all_price_requests(self):
        """Fetches all records from the price_requests table."""
        try:
            with get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM price_requests
                    ORDER BY id
                """)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Database Error (get_all_price_requests): {e}")
            return []

    def get_availability_notifications(self, email):
        """Fetches all availability notifications for a given email."""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT id, product_name, product_link 
                FROM availability_requests 
                WHERE email = %s
                ORDER BY id
            """, (email,))
            return cursor.fetchall()

    def get_price_notifications(self, email):
        """Fetches all price notifications for a given email."""
        with get_cursor() as cursor:
            cursor.execute("""
                SELECT id, product_name, product_link, target_price 
                FROM price_requests 
                WHERE email = %s
                ORDER BY id
            """, (email,))
            return cursor.fetchall()

    def delete_request(self, notification_id, email, notification_type):
        """Deletes a notification from the database by ID and email."""
        try:
            with get_cursor(commit=True) as cursor:
                if notification_type == "availability":
                    cursor.execute("""
                        DELETE FROM availability_requests 
                        WHERE id = %s AND email = %s
                    """, (notification_id, email))
                elif notification_type == "price":
                    cursor.execute("""
                        DELETE FROM price_requests 
                        WHERE id = %s AND email = %s
                    """, (notification_id, email))
                return True
        except psycopg2.Error as e:
            print(f"Database Error (delete_request): {e}")
            return False
    
    def batch_get_requests(self, batch_size=100):
        """Get requests in batches to process more efficiently."""
        try:
            with get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM availability_requests
                    LIMIT {batch_size}
                """)
                availability_requests = cursor.fetchall()
                
                cursor.execute(f"""
                    SELECT * FROM price_requests
                    LIMIT {batch_size}
                """)
                price_requests = cursor.fetchall()
                
            return availability_requests, price_requests
        except psycopg2.Error as e:
            print(f"Database Error (batch_get_requests): {e}")
            return [], []
    
    def close_pool():
        """Close the connection pool when shutting down the application."""
        if connection_pool:
            connection_pool.closeall()
            print("Database connection pool closed.")