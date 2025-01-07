from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from setting import ALLOWED_USER, NOTIFY_USER_ID

# Access Control Decorator
def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id == ALLOWED_USER:
            await update.message.reply_text("You are not authorized to use this bot.")
            user = update.effective_user()
            await notify_to_admin(user, context)
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

async def notify_to_admin (user, context: ContextTypes.DEFAULT_TYPE):
    message = f"User {user.first_name} {user.last_name} (ID: {user.id} , Bot: {user.is_bot}) just used the bot."
    await context.bot.send_message(NOTIFY_USER_ID, message)