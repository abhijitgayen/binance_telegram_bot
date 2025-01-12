import sqlite3
import json

class Database:
    def __init__(self, db_name="bot_data.db"):
        """Initializes the Database with the given name."""
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name,check_same_thread=False)
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
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ads (
                advNo TEXT  PRIMARY KEY,             
                price REAL NOT NULL,                
                surplusAmount REAL NOT NULL,         
                minSingleTransAmount REAL NOT NULL,  
                maxSingleTransAmount REAL NOT NULL,   
                tradeType TEXT NOT NULL,             
                minSingleTransQuantity REAL NOT NULL,  
                maxSingleTransQuantity REAL NOT NULL,
                apiResponseCode TEXT,
                apiResponseMessage TEXT,
                data TEXT,  -- Column for storing JSON data
                createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- auto set on insert
                updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
         """)
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

        print(bot_config_json, 'bot_config_json')
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
    
    def insert_ad(self, ads):
        """Insert a single ad record into the database."""
        try:
            ads_data = []
            for ad in ads:
                adv = ad.get('adv', {})
        
                # Extract relevant fields
                adv_no = adv.get('advNo')
                price = float(adv.get('price', 0))
                surplus_amount = float(adv.get('surplusAmount', 0))
                min_single_trans_amount = float(adv.get('minSingleTransAmount', 0))
                max_single_trans_amount = float(adv.get('maxSingleTransAmount', 0))
                trade_type = adv.get('tradeType')
                min_single_trans_quantity = float(adv.get('minSingleTransQuantity', 0))
                max_single_trans_quantity = float(adv.get('maxSingleTransQuantity', 0))
                api_response_code = None  # Placeholder for API response code
                api_response_message = None  # Placeholder for API response message
                data = json.dumps(ad)  # Serialize the entire ad as JSON

                # Add to the list of data to insert
                ads_data.append((
                    adv_no, price, surplus_amount, min_single_trans_amount, max_single_trans_amount,
                    trade_type, min_single_trans_quantity, max_single_trans_quantity, data
                ))
            
            # self.cursor.executemany("""
            #     INSERT INTO ads (
            #         advNo, price, surplusAmount, minSingleTransAmount, maxSingleTransAmount,
            #         tradeType, minSingleTransQuantity, maxSingleTransQuantity, data
            #     )
            #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            #     ON CONFLICT(data)
            #     DO UPDATE SET
            #         surplusAmount = excluded.surplusAmount,
            #         minSingleTransAmount = excluded.minSingleTransAmount,
            #         maxSingleTransAmount = excluded.maxSingleTransAmount,
            #         tradeType = excluded.tradeType,
            #         minSingleTransQuantity = excluded.minSingleTransQuantity,
            #         maxSingleTransQuantity = excluded.maxSingleTransQuantity,
            #         apiResponseCode = NULL,
            #         apiResponseMessage = NULL,
            #         data = excluded.data,
            #         updatedAt = CURRENT_TIMESTAMP
            # """, ads_data)

            self.cursor.executemany("""
                INSERT INTO ads (
                    advNo, price, surplusAmount, minSingleTransAmount, maxSingleTransAmount,
                    tradeType, minSingleTransQuantity, maxSingleTransQuantity, data
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(advNo)
                DO UPDATE SET
                    price = CASE 
                            WHEN ads.data != excluded.data THEN excluded.price
                            ELSE ads.price
                            END,
                    surplusAmount = CASE 
                                    WHEN ads.data != excluded.data THEN excluded.surplusAmount
                                    ELSE ads.surplusAmount
                                    END,
                    minSingleTransAmount = CASE 
                                        WHEN ads.data != excluded.data THEN excluded.minSingleTransAmount
                                        ELSE ads.minSingleTransAmount
                                        END,
                    maxSingleTransAmount = CASE 
                                        WHEN ads.data != excluded.data THEN excluded.maxSingleTransAmount
                                        ELSE ads.maxSingleTransAmount
                                        END,
                    tradeType = CASE 
                                WHEN ads.data != excluded.data THEN excluded.tradeType
                                ELSE ads.tradeType
                                END,
                    minSingleTransQuantity = CASE 
                                            WHEN ads.data != excluded.data THEN excluded.minSingleTransQuantity
                                            ELSE ads.minSingleTransQuantity
                                            END,
                    maxSingleTransQuantity = CASE 
                                            WHEN ads.data != excluded.data THEN excluded.maxSingleTransQuantity
                                            ELSE ads.maxSingleTransQuantity
                                            END,
                    data = CASE 
                            WHEN ads.data != excluded.data THEN excluded.data
                            ELSE ads.data
                            END,
                    apiResponseCode = CASE 
                                    WHEN ads.data != excluded.data THEN NULL
                                    ELSE ads.apiResponseCode
                                    END,
                    apiResponseMessage = CASE 
                                        WHEN ads.data != excluded.data THEN NULL
                                        ELSE ads.apiResponseMessage
                                        END,
                    updatedAt = CURRENT_TIMESTAMP  -- Update timestamp when any field changes
                """, ads_data)

            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while inserting ads: {e}")
    
    def update_ads_response(self, adv_no, response_code, response_message):
        """Update the API response for a specific ad in the database."""
        try:
            # Execute the update query for the given advNo
            self.cursor.execute("""
                UPDATE ads
                SET apiResponseCode = ?,
                    apiResponseMessage = ?,
                    updatedAt = CURRENT_TIMESTAMP
                WHERE advNo = ?
            """, (response_code, response_message, adv_no))
            
            # Commit the changes to the database
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred while updating ad response: {e}")

    def delete_all_ads(self):
        """Delete all ads from the database."""
        try:
            # Execute the delete query
            self.cursor.execute("DELETE FROM ads")
            
            # Commit the changes to the database
            self.conn.commit()
            
            print("All ads have been deleted.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting ads: {e}")


    def get_filtered_ads(self, extra_filter):
        # Construct the SQL query with dynamic filtering
        query = "SELECT * FROM ads WHERE 1=1"
        params = []

        # Add filters to the query
        if extra_filter.get("price") is not None:
            query += " AND price < ?"
            params.append(extra_filter["price"])
        if extra_filter.get("minimum_limit") is not None:
            query += " AND maxSingleTransAmount >= ?"
            params.append(extra_filter["minimum_limit"])
        if extra_filter.get("maximum_limit") is not None:
            query += " AND minSingleTransAmount <= ?"
            params.append(extra_filter["maximum_limit"])
        if extra_filter.get("error_codes"):
            error_codes = extra_filter["error_codes"]
            if isinstance(error_codes, str):
                error_codes = [error_codes]
            elif not isinstance(error_codes, list):
                raise ValueError("error_codes must be string or list")
                
            placeholders = ','.join('?' * len(error_codes))
            query += f" AND (apiResponseCode NOT IN ({placeholders}) OR apiResponseCode IS NULL)"
            params.extend(error_codes)

        query += " ORDER BY createdAt DESC"

        # Execute the query
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        # Get column names
        column_names = [description[0] for description in self.cursor.description]

        # Convert rows to dictionaries
        ads = []
        for row in rows:
            ad = dict(zip(column_names, row))
            # Deserialize the JSON data column
            if 'data' in ad and ad['data']:
                ad['data'] = json.loads(ad['data'])
            ads.append(ad)

        return ads
    

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


