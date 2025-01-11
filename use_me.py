from setting import TELEGRAM_TOKEN, ALLOWED_USER
import requests

def send_telegram_message():
    """Send a message to the configured Telegram chat."""
    if not TELEGRAM_TOKEN or not ALLOWED_USER:
        print("Telegram configuration missing. Skipping Telegram message.")
        return

    message = "Hey Flok! 👋 I'm here to make your work easier and more fun! 🚀 \n\nPowered by Abhijit. 💡 \n\nTap /start to get things rolling!"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": ALLOWED_USER,
        "text": message,
        "parse_mode": "Markdown",
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Telegram message sent successfully.")
        else:
            print(f"Failed to send Telegram message. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

send_telegram_message()