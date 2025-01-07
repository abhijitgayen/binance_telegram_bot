
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv ('TELEGRAM_TOKEN')
ALLOWED_USER = os.getenv("ALLOWED_USER","")
NOTIFY_USER_ID = os.getenv ('NOTIFY_USER_ID')

DEFAULT_BOT_CONFIG = {
    "ASSET": "USDT",
    "FIAT": "INR",
    "PAGE": 2,
    "ROWS": 20,
    "TRADE_TYPE": "BUY",
    "TOTAL_AMOUNT_TO_INVEST": 10000,
    "NO_OF_ORDERS": 1,
    "EXTRA_FILTER": {
        "price": 85,
        "minimum_limit": 100,
        "maximum_limit": 1000
    },
    "API_KEY": "",
    "SECRET_KEY": ""
}