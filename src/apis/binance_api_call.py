import time
import hmac
import hashlib
import requests
from src.db.init import Database
from telegram import Update
from setting import CREATE_ORDER_SLEEP
from src.helpers.notify import direct_notify_admin

class BinanceApiCall:
    def __init__(self, base_url):
        """Initialize the bot with API details."""
        self.base_url = base_url
        self.config = None
        self.amount_spend = 0
        self.remaining_amount = 0
        self.order = 0
        self.sleep_time = CREATE_ORDER_SLEEP

    def set_config (self, config):
        #TODO:  need to add validator of the config
        self.api_key = config.get("API_KEY")
        self.secret_key = config.get("SECRET_KEY")
        self.config = config

    def _generate_signature(self, query_string):
        """Generate HMAC SHA256 signature."""
        return hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()

    def _send_request(self, endpoint, query_string, body=None):
        """Send a POST request to the Binance API."""
        signature = self._generate_signature(query_string)
        headers = {
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
        response = requests.post(url, headers=headers, json=body)
        return response.json()

    def _search_ads(self, asset, fiat, page, rows, trade_type):
        """Search for ads based on specified criteria."""
        timestamp = int(time.time() * 1000)
        query_string = f"asset={asset}&fiat={fiat}&page={page}&rows={rows}&tradeType={trade_type}&timestamp={timestamp}"
        body = {
            "asset": asset,
            "fiat": fiat,
            "page": page,
            "rows": rows,
            "tradeType": trade_type
        }
        return self._send_request("/sapi/v1/c2c/ads/search", query_string, body)

    def _place_order(self, adv_order_number, asset, buy_type, fiat_unit, match_price, total_amount, trade_type):
        """Place an order based on ad details."""
        timestamp = int(time.time() * 1000)
        query_string = f"advOrderNumber={adv_order_number}&asset={asset}&buyType={buy_type}&fiatUnit={fiat_unit}&timestamp={timestamp}"
        body = {
            "advOrderNumber": adv_order_number,
            "asset": asset,
            "buyType": buy_type,
            "fiatUnit": fiat_unit,
            "matchPrice": match_price,
            "totalAmount": total_amount,
            "tradeType": trade_type,
            "buyType": "BY_MONEY",
            "origin": "MAKE_TAKE",
        }
        return self._send_request("/sapi/v1/c2c/orderMatch/placeOrder", query_string, body) 

    def search_ads_jobs(self, callback = None):
        """Main logic to search ads and place an order."""

        if not self.config:
            print('Error: Config not there')
            return
        
        CONFIG_ASSET = self.config.get("ASSET", "USDT")
        CONFIG_FIAT = self.config.get("FIAT", "INR")
        CONFIG_PAGE = self.config.get("PAGE", 1)
        CONFIG_ROWS = self.config.get("ROWS", 10)
        CONFIG_TRADE_TYPE = self.config.get("TRADE_TYPE", "BUY")

        # Q: where need to implement EXTRA_FILTER at the time read ads from db
        # EXTRA_FILTER = self.config.get("EXTRA_FILTER", {})

        print("Searching for ads...")
        ads = self._search_ads(CONFIG_ASSET, CONFIG_FIAT, CONFIG_PAGE, CONFIG_ROWS, CONFIG_TRADE_TYPE)
        if "data" in ads and ads.get("data"):
            return ads
        else:
            print("Something went wrong while fetching ads.")
            print(f"CODE: {ads.get('code', 'N/A')}")
            print(f"ERROR: {ads.get('msg', 'Unknown error occurred.')}")
            return {
                "error_code": ads.get('code', 'N/A'),
                "error_message": ads.get('msg', 'Unknown error occurred.')
            }
        
    def _get_order_amount(self, match_price, max_single_trans_amount, min_single_trans_amount, total_surplus_amount):
        """Calculate the maximum possible order amount based on surplus and transaction limits."""
        min_surplus_amount = min_single_trans_amount / match_price
        max_surplus_amount = max_single_trans_amount / match_price

        surplus_amount = max(min_surplus_amount, min(max_surplus_amount, total_surplus_amount))
        max_possible_amount = surplus_amount * match_price
        return max_possible_amount

    async def create_orders_jobs(self, db: Database, update: Update , callback = None):
        """Iterate through the filtered ads and place orders."""
        ads = db.get_filtered_ads(self.config.get("EXTRA_FILTER"))
        if not self.config:
            print('Error: Config not there')
            return
        
        CONFIG_ASSET = self.config.get("ASSET", "USDT")
        CONFIG_FIAT = self.config.get("FIAT", "INR")
        TOTAL_AMOUNT_TO_INVEST = self.config.get("TOTAL_AMOUNT_TO_INVEST", 0)
        NO_OF_ORDERS = self.config.get("NO_OF_ORDERS", 1)
        TRADE_TYPE = self.config.get("TRADE_TYPE", "BUY")

        self.remaining_amount = TOTAL_AMOUNT_TO_INVEST

        for index, adv in enumerate(ads):
            adv_order_number = adv.get("advNo")
            match_price = float(adv.get("price", 0))
            surplus_amount = float(adv.get("surplusAmount", 0))
            min_single_trans_amount = float(adv.get("minSingleTransAmount", 0))
            max_single_trans_amount = float(adv.get("maxSingleTransAmount", 0))

            total_amount = self._get_order_amount(match_price, max_single_trans_amount, min_single_trans_amount, surplus_amount)
            order_message =f"📄 Order Number: {adv_order_number}\n💰 Match Price: {match_price:.2f}\n📦 Surplus Amount: {surplus_amount:.2f}\n🔢 Transaction Limits: {min_single_trans_amount:.2f} - {max_single_trans_amount:.2f}\n💴 Total Amount: {total_amount}\n" 

            if total_amount > self.remaining_amount:
                if self.remaining_amount > min_single_trans_amount:
                    total_amount = self.remaining_amount
                else:
                    message = f" 🛑 Inappropriate Amount 🛑 \n\n {order_message}"
                    await update.message.reply_text(message, parse_mode="Markdown")
                    continue

            response_place_order =  self._place_order(
                adv_order_number=adv_order_number,
                asset=CONFIG_ASSET,
                buy_type="BY_AMOUNT",
                fiat_unit=CONFIG_FIAT,
                match_price=match_price,
                total_amount=total_amount,
                trade_type=TRADE_TYPE
            )

            if response_place_order.get("success") is True:
                order_message = f"""
                    *📝 Order Information:*

                    📋 *Order Number:* `{response_place_order.get('orderNumber', 'N/A')}`
                    📋 *Adv Order Number:* `{response_place_order.get('advOrderNumber', 'N/A')}`

                    ⏳ *Allow Complain Time:* `{response_place_order.get('allowComplainTime', 'N/A')}`
                    🧑‍💻 *User Id:* `{response_place_order.get('userId', 'N/A')}`
                    👤 *Adv User Id:* `{response_place_order.get('advUserId', 'N/A')}`

                    🛍️ *Buyer Information:*
                    - *Nickname:* `{response_place_order.get('buyerNickname', 'N/A')}`
                    - *Name:* `{response_place_order.get('buyerName', 'N/A')}`

                    💰 *Transaction Details:*
                    - *Amount:* `{response_place_order.get('amount', 'N/A')} {response_place_order.get('asset', 'N/A')}`
                    - *Price:* `{response_place_order.get('price', 'N/A')} {response_place_order.get('fiatUnit', 'N/A')}/{response_place_order.get('asset', 'N/A')}`
                    - *Total Price:* `{response_place_order.get('totalPrice', 'N/A')} {response_place_order.get('fiatUnit', 'N/A')}`

                    💼 *Trade Information:*
                    - *Trade Type:* `{response_place_order.get('tradeType', 'N/A')}`
                    - *Pay Type:* `{response_place_order.get('payType', 'N/A')}`
                    """
                message = f"✅ Order placed successfully ✅ \n\n {order_message}\n {order_message}"
                await update.message.reply_text(message, parse_mode="Markdown")
            
                self.order += 1
                self.amount_spend += total_amount
                self.remaining_amount -= total_amount
                direct_notify_admin(message)

            else:
                error_message = response_place_order.get("msg", "Unknown error occurred.")
                error_code = response_place_order.get('code', 'N/A')
                message = f"🛑 Order Fail 🛑 \n\n {order_message} \nERR CODE: {error_code}\nERR MSG: {error_message}"
                await update.message.reply_text(message, parse_mode="Markdown")
                db.update_ads_response(adv_no=adv_order_number, response_code=error_code, response_message=error_message)

                req_body = {
                    "advOrderNumber": adv_order_number,
                    "asset": CONFIG_ASSET,
                    "fiatUnit": CONFIG_FIAT,
                    "matchPrice": match_price,
                    "totalAmount": total_amount,
                    "tradeType": TRADE_TYPE,
                    "buyType": "BY_MONEY",
                    "origin": "MAKE_TAKE",
                    "adv": adv
                }

                direct_notify_admin(message,req_body)
            
            if self.order >= NO_OF_ORDERS or self.amount_spend > TOTAL_AMOUNT_TO_INVEST:
                if callback:
                    callback ()
                print("Order limit reached. Stopping further orders.")
                break

            if index < len(ads) - 1:
                print(f"Waiting for {self.sleep_time} seconds before placing the next order...")
                time.sleep(self.sleep_time)
