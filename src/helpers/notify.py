from telegram.ext import ContextTypes
from datetime import datetime
import requests
import json
from setting import TELEGRAM_TOKEN, NOTIFY_USER_ID

async def notify_admin(context: ContextTypes.DEFAULT_TYPE, error_type: str, details: str, **kwargs):
    """Send notification to admin for errors/important events"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = (
        f"🚨 *{error_type}* 🚨\n\n"
        f"*Time:* `{current_time}`\n"
        f"*Details:* {details}\n"
    )
    
    # Add any additional info from kwargs
    for key, value in kwargs.items():
        message += f"*{key}:* `{value}`\n"
        
    await context.bot.send_message(
        chat_id=NOTIFY_USER_ID,
        text=message,
        parse_mode="Markdown"
    )

def direct_notify_admin(message, req_body={}, need_pin=False):
    try:
        json_message = json.dumps(req_body, indent=2)

        # Prepare the payload for the Telegram API
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": NOTIFY_USER_ID,
            "text": f"{message} \n\n<pre>{json_message}</pre>",
            "parse_mode": "HTML",  # Use HTML to preserve JSON formatting
            "disable_notification": True
        }

        # Send the message using a POST request
        response = requests.post(url, json=payload)

        # Check and log response
        if response.status_code == 200:
            print("Message sent successfully!")

            if need_pin:
                message_id = response.json().get("result", {}).get("message_id")
                # Pin the message
                pin_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/pinChatMessage"
                pin_payload = {
                    "chat_id": NOTIFY_USER_ID,
                    "message_id": message_id,
                    "disable_notification": True
                }
                pin_response = requests.post(pin_url, json=pin_payload)

                if pin_response.status_code == 200:
                    print("Message pinned successfully!")
                else:
                    print("Failed to pin the message:")
        else:
            print("Failed to send message:", response.text)

        return response.json()
    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}
