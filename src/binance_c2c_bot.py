import time
import hmac
import hashlib
import requests

class BinanceC2CBot:
    def __init__(self, base_url, api_key, secret_key, sleep_time=10):
        """Initialize the bot with API details."""
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.sleep_time = sleep_time
        self.amount_spend = 0
        self.remaining_amount = 0
        self.order = 0

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

    def search_ads(self, asset, fiat, page, rows, trade_type, extra_filter=None):
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
        ads = self._send_request("/sapi/v1/c2c/ads/search", query_string, body)
        return self.filter_ads(ads, extra_filter)

    def filter_ads(self, ads, extra_filter):
        """Filter the ads based on price and transaction limits."""
        if "data" not in ads or not ads["data"]:
            return {"data": []}
        
        filtered_ads = {"data": []}
        filtered_ads["data"] = [
            ad for ad in ads["data"]
            if (
                (extra_filter.get("price") is None or float(ad.get("adv", {}).get("price", float("inf"))) < extra_filter.get("price"))
                and
                (extra_filter.get("minimum_limit") is None or float(ad.get("adv", {}).get("maxSingleTransAmount", float("inf"))) >= extra_filter.get("minimum_limit"))
                and
                (extra_filter.get("maximum_limit") is None or float(ad.get("adv", {}).get("minSingleTransAmount", float("inf"))) <= extra_filter.get("maximum_limit"))
            )
        ]
        return filtered_ads

    def place_order(self, adv_order_number, asset, buy_type, fiat_unit, match_price, total_amount, trade_type):
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
            "buyType": "BY_AMOUNT",
            "origin": "MAKE_TAKE",
        }
        return self._send_request("/sapi/v1/c2c/orderMatch/placeOrder", query_string, body)

    def get_order_amount(self, match_price, max_single_trans_amount, min_single_trans_amount, total_surplus_amount):
        """Calculate the maximum possible order amount based on surplus and transaction limits."""
        min_surplus_amount = min_single_trans_amount / match_price
        max_surplus_amount = max_single_trans_amount / match_price

        surplus_amount = max(min_surplus_amount, min(max_surplus_amount, total_surplus_amount))
        max_possible_amount = surplus_amount * match_price
        return max_possible_amount

    def create_orders(self, ads, config):
        """Iterate through the filtered ads and place orders."""
        CONFIG_ASSET = config.get("ASSET", "USDT")
        CONFIG_FIAT = config.get("FIAT", "INR")
        TOTAL_AMOUNT_TO_INVEST = config.get("TOTAL_AMOUNT_TO_INVEST", 0)
        NO_OF_ORDERS = config.get("NO_OF_ORDERS", 1)

        self.remaining_amount = TOTAL_AMOUNT_TO_INVEST

        for index, adv in enumerate(ads.get("data")):
            adv_details = adv.get("adv", {})
            adv_order_number = adv_details.get("advNo")
            match_price = float(adv_details.get("price", 0))
            surplus_amount = float(adv_details.get("surplusAmount", 0))
            min_single_trans_amount = float(adv_details.get("minSingleTransAmount", 0))
            max_single_trans_amount = float(adv_details.get("maxSingleTransAmount", 0))

            total_amount = self.get_order_amount(match_price, max_single_trans_amount, min_single_trans_amount, surplus_amount)

            print(f"\nPlacing order: AD order No={adv_order_number}, Price={match_price} {CONFIG_FIAT}/{CONFIG_ASSET}, Amount={total_amount} {CONFIG_FIAT}\n")

            if total_amount > self.remaining_amount:
                if self.remaining_amount > min_single_trans_amount:
                    total_amount = self.remaining_amount
                else:
                    print('\nInappropriate Amount')
                    continue

            response_place_order = self.place_order(
                adv_order_number=adv_order_number,
                asset=CONFIG_ASSET,
                buy_type="BY_AMOUNT",
                fiat_unit=CONFIG_FIAT,
                match_price=match_price,
                total_amount=total_amount,
                trade_type=config.get("TRADE_TYPE", "BUY")
            )

            if response_place_order.get("success") is True:
                print("Order placed successfully!")
                self.order += 1
                self.amount_spend += total_amount
                self.remaining_amount -= total_amount

            else:
                error_message = response_place_order.get("msg", "Unknown error occurred.")
                print(f"Failed to place order. Error Code: {response_place_order.get('code', 'N/A')}, Error Message: {error_message}")

            if self.order >= NO_OF_ORDERS or self.amount_spend > TOTAL_AMOUNT_TO_INVEST:
                print("Order limit reached. Stopping further orders.")
                break

            if index < len(ads.get("data")) - 1:
                print(f"Waiting for {self.sleep_time} seconds before placing the next order...")
                time.sleep(self.sleep_time)

    def run(self, config):
        """Main logic to search ads and place an order."""
        CONFIG_ASSET = config.get("ASSET", "USDT")
        CONFIG_FIAT = config.get("FIAT", "INR")
        CONFIG_PAGE = config.get("PAGE", 1)
        CONFIG_ROWS = config.get("ROWS", 10)
        CONFIG_TRADE_TYPE = config.get("TRADE_TYPE", "BUY")
        EXTRA_FILTER = config.get("EXTRA_FILTER", {})

        print("Searching for ads...")
        ads = self.search_ads(CONFIG_ASSET, CONFIG_FIAT, CONFIG_PAGE, CONFIG_ROWS, CONFIG_TRADE_TYPE, EXTRA_FILTER)

        if "data" in ads and ads.get("data"):
            print(f"AD found: {len(ads.get('data', []))}")
            print(f"Total Available Ads: {ads.get('total', 0)}")
            
            print(f"Filtered ads count: {len(ads['data'])}")
            
            self.create_orders(ads, config)
        else:
            print("Something went wrong while fetching ads.")
            print(f"CODE: {ads.get('code', 'N/A')}")
            print(f"ERROR: {ads.get('msg', 'Unknown error occurred.')}")
