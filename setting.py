
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv ('TELEGRAM_TOKEN')
ALLOWED_USER = os.getenv("ALLOWED_USER","")
NOTIFY_USER_ID = os.getenv ('NOTIFY_USER_ID')
LIST_ADS_SLEEP = int(os.getenv('LIST_ADS_SLEEP', '5'))
CREATE_ORDER_SLEEP = int(os.getenv('CREATE_ORDER_SLEEP', '9')) 
BINANCE_API_URL = os.getenv('BINANCE_API_URL')

DEFAULT_BOT_CONFIG = {
    "ASSET": "USDT",
    "FIAT": "INR",
    "PAGE": 1,
    "ROWS": 20,
    "TRADE_TYPE": "BUY",
    "TOTAL_AMOUNT_TO_INVEST": 10000,
    "NO_OF_ORDERS": 1,
    "EXTRA_FILTER": {
        "price": 85,
        "minimum_limit": 100,
        # "maximum_limit": 1000,
        "error_codes": ["83999"]
    },
    "API_KEY": "",
    "SECRET_KEY": ""
}