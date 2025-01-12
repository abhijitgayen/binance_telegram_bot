from telegram.ext import ContextTypes
from setting import NOTIFY_USER_ID
from datetime import datetime

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