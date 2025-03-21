import psycopg2
from psycopg2 import pool
import contextlib
import os

class DatabaseHandler:
    """Handles database operations with connection pooling."""
    
    # Class variable for the connection pool
    _connection_pool = None
    
    @classmethod
    def initialize_pool(cls, min_conn=5, max_conn=20, database_url=None):
        """Initialize the connection pool with configurable parameters."""
        if cls._connection_pool is not None:
            print("Connection pool already initialized")
            return
            
        # Use environment variable or passed URL
        database_url = database_url or os.environ.get('DATABASE_URL') or \
            "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"
            
        try:
            cls._connection_pool = pool.ThreadedConnectionPool(
                minconn=min_conn,
                maxconn=max_conn,
                dsn=database_url
            )
            print(f"Connection pool initialized with min={min_conn}, max={max_conn}")
        except psycopg2.Error as e:
            print(f"Error initializing connection pool: {e}")
            raise
    
    @classmethod
    def get_connection_pool(cls):
        """Get the connection pool, initializing it if necessary."""
        if cls._connection_pool is None:
            cls.initialize_pool()
        return cls._connection_pool
    
    @classmethod
    def close_pool(cls):
        """Close the connection pool when shutting down the application."""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            cls._connection_pool = None
            print("Database connection pool closed.")
    
    @classmethod
    @contextlib.contextmanager
    def get_db_connection(cls):
        """Get a database connection from the pool using context manager for automatic cleanup."""
        conn = None
        try:
            conn = cls.get_connection_pool().getconn()
            # Simple connection validation
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            yield conn
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            if conn:
                # If connection is broken, don't return it to the pool
                cls.get_connection_pool().putconn(conn, close=True)
                conn = None
            raise
        finally:
            if conn:
                cls.get_connection_pool().putconn(conn)
    
    @classmethod
    @contextlib.contextmanager
    def get_cursor(cls, commit=False):
        """Get a cursor using the connection from the pool."""
        with cls.get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except psycopg2.Error as e:
                conn.rollback()
                print(f"Database cursor error: {e}")
                raise
            finally:
                cursor.close()

    def check_availability_exists(self, email, product_link):
        """Checks if an availability request already exists for the given email and product link."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM availability_requests WHERE email = %s AND product_link = %s)
            """, (email, product_link))
            exists = cursor.fetchone()[0]
            
            # ✅ Debug Logging
            # print(f"[DEBUG] Checking availability existence for Email: {email}, Product Link: {product_link} → Exists: {exists}")
            
            return exists

    def check_price_exists(self, email, product_link):
        """Checks if a price request already exists for the given email and product link."""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM price_requests WHERE email = %s AND product_link = %s)
            """, (email, product_link))
            exists = cursor.fetchone()[0]

            # ✅ Debug Logging
            # print(f"[DEBUG] Checking price existence for Email: {email}, Product Link: {product_link} → Exists: {exists}")
            
            return exists

    
    def store_availability_request(self, email, product_link, name, shoesize):
        """Inserts an availability request into the database if it doesn't exist."""
        try:
            # First check if this request already exists
            if self.check_availability_exists(email, product_link):
                return False, "An availability request for this product already exists."
                
            with self.get_cursor(commit=True) as cursor:
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
                
            with self.get_cursor(commit=True) as cursor:
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
            with self.get_cursor() as cursor:
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
            with self.get_cursor() as cursor:
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
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT id, product_name, product_link 
                FROM availability_requests 
                WHERE email = %s
                ORDER BY id
            """, (email,))
            return cursor.fetchall()

    def get_price_notifications(self, email):
        """Fetches all price notifications for a given email."""
        with self.get_cursor() as cursor:
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
            with self.get_cursor(commit=True) as cursor:
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
            with self.get_cursor() as cursor:
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