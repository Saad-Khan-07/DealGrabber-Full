import psycopg2

class DatabaseHandler:
    def __init__(self):
        """Initialize database connection."""
        self.DATABASE_URL = "postgresql://postgres:GUKqWbRSZZPXlHzPZXWiGgfpvszUsvVq@trolley.proxy.rlwy.net:41936/railway"
        self.conn = psycopg2.connect(self.DATABASE_URL)
        self.cursor = self.conn.cursor()

    def store_availability_request(self, email, product_link, name, shoesize):
        """Inserts an availability request into the database."""
        self.cursor.execute("""
            INSERT INTO availability_requests (email, product_link, product_name, shoesize)
            VALUES (%s, %s, %s, %s)
        """, (email, product_link, name, shoesize))
        self.conn.commit()

    def store_price_request(self, email, product_link, name, target_price, shoesize):
        """Inserts a price request into the database."""
        self.cursor.execute("""
            INSERT INTO price_requests (email, product_link, product_name, target_price, shoesize)
            VALUES (%s, %s, %s, %s, %s)
        """, (email, product_link, name, target_price, shoesize))
        self.conn.commit()

    def get_all_availability_requests(self):
        """Fetches all records from the availability_requests table."""
        self.cursor.execute("SELECT * FROM availability_requests")
        return self.cursor.fetchall()

    def get_all_price_requests(self):
        """Fetches all records from the price_requests table."""
        self.cursor.execute("SELECT * FROM price_requests")
        return self.cursor.fetchall()

    def close_connection(self):
        """Closes the database connection."""
        self.cursor.close()
        self.conn.close()