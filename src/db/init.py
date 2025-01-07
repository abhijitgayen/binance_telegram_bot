import sqlite3
import json

class Database:
    def __init__(self, db_name="bot_data.db"):
        """Initializes the Database with the given name."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        """Creates a table if it doesn't already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                bot_config TEXT  -- Column for storing JSON data
            )
        """)
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS ads (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         adv_order_number TEXT,
        #         price REAL,
        #         surplus_amount REAL,
        #         min_single_trans_amount REAL,
        #         max_single_trans_amount REAL,
        #         nick_name TEXT,
        #         user_no TEXT,
        #         trade_methods TEXT,
        #         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        #     )
        # """)
        # self.cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS order_responses (
        #         id INTEGER PRIMARY KEY AUTOINCREMENT,
        #         order_number TEXT,
        #         adv_order_number TEXT,
        #         buyer_nickname TEXT,
        #         buyer_name TEXT,
        #         asset TEXT,
        #         fiat_unit TEXT,
        #         amount REAL,
        #         price REAL,
        #         total_price REAL,
        #         trade_type TEXT,
        #         pay_type TEXT,
        #         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        #     )
        # """)
        self.conn.commit()

    def insert_user(self, user_id, first_name, last_name, extra_info=None):
        """Inserts a new user into the users table along with JSON data."""
        bot_config_json = json.dumps(extra_info) if extra_info else None  # Convert dictionary to JSON string
        self.cursor.execute('''
            INSERT OR IGNORE INTO users (id, first_name, last_name, bot_config)
            VALUES (?, ?, ?, ?)
        ''', (user_id, first_name, last_name, bot_config_json))
        self.conn.commit()

    def insert_or_update_user(self, user_id, first_name, last_name, extra_info=None):
        """Inserts a new user or updates an existing user in the users table."""
        bot_config_json = json.dumps(extra_info) if extra_info else None  # Convert dictionary to JSON string
        self.cursor.execute('''
            INSERT INTO users (id, first_name, last_name, bot_config)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) 
            DO UPDATE SET
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                bot_config = excluded.bot_config
        ''', (user_id, first_name, last_name, bot_config_json))
        self.conn.commit()


    def update_bot_config (self, user_id, bot_config):
        bot_config_json = json.dumps(bot_config)
        self.cursor.execute('''
            UPDATE users
            SET bot_config = ?
            WHERE id = ?
        ''', (bot_config_json, user_id))
        self.conn.commit()

    def get_user(self, user_id):
        """Fetches a user and their JSON data from the users table."""
        self.cursor.execute('''
            SELECT id, first_name, last_name, bot_config FROM users WHERE id = ?
        ''', (user_id,))
        row = self.cursor.fetchone()
        if row:
            user_data = {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'bot_config': json.loads(row[3]) if row[3] else None  # Convert JSON string back to dictionary
            }
            return user_data
        return None
    






    
    def insert_ad(self, ad):
        """Insert a single ad record into the database."""
        self.cursor.execute("""
            INSERT INTO ads (
                adv_order_number, price, surplus_amount, 
                min_single_trans_amount, max_single_trans_amount, 
                nick_name, user_no, trade_methods
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ad.get("adv_order_number"),
            ad.get("price"),
            ad.get("surplus_amount"),
            ad.get("min_single_trans_amount"),
            ad.get("max_single_trans_amount"),
            ad.get("nick_name"),
            ad.get("user_no"),
            ad.get("trade_methods")
        ))
        self.connection.commit()

    def insert_order_response(self, order_response):
        """Insert an order response into the database."""
        self.cursor.execute("""
            INSERT INTO order_responses (
                order_number, adv_order_number, buyer_nickname, 
                buyer_name, asset, fiat_unit, amount, 
                price, total_price, trade_type, pay_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_response.get("order_number"),
            order_response.get("adv_order_number"),
            order_response.get("buyer_nickname"),
            order_response.get("buyer_name"),
            order_response.get("asset"),
            order_response.get("fiat_unit"),
            order_response.get("amount"),
            order_response.get("price"),
            order_response.get("total_price"),
            order_response.get("trade_type"),
            order_response.get("pay_type")
        ))
        self.connection.commit()

    def list_ads_with_filters(self, **filters):
        query = "SELECT * FROM ads WHERE 1=1"
        params = []

        # Apply filters
        if "price_max" in filters:
            query += " AND price <= ?"
            params.append(filters["price_max"])

        # Execute query
        query += " ORDER BY timestamp DESC"
        self.cursor.execute(query, params)
        ads = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "adv_order_number": row[1],
                "price": row[2],
                "surplus_amount": row[3],
                "min_single_trans_amount": row[4],
                "max_single_trans_amount": row[5],
                "nick_name": row[6],
                "user_no": row[7],
                "trade_methods": row[8],
                "timestamp": row[9]
            }
            for row in ads
        ]
    


    def close(self):
        """Closes the database connection."""
        self.conn.close()


