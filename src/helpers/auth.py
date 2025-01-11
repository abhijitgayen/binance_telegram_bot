from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from setting import ALLOWED_USER, NOTIFY_USER_ID
from datetime import datetime
from src.db.init import Database


# Access Control Decorator
def restricted(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_user.id != ALLOWED_USER:
            await update.message.reply_text(
                "🚫 *Access Denied*\n\n"
                "You are not authorized to use this bot. "
                "If you believe this is an error,\nplease contact the administrator.",
                parse_mode='Markdown'
            )
            user = update.effective_user
            await notify_to_admin(user, context)
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

async def notify_to_admin (user, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = (
        f"🚨 **Security Alert!** 🚨\n\n"
        f"**User:** [{user.first_name} {user.last_name}](tg://user?id={user.id})\n"
        f"**User ID:** `{user.id}`\n"
        f"**Bot User:** {'Yes ✅' if user.is_bot else 'No ❌'}\n\n"
        f"**Action:** Unauthorized access attempt detected.\n"
        f"**Time:** {current_time}\n\n"
        f"Please review this activity immediately."
    )
    await context.bot.send_message(NOTIFY_USER_ID, message, parse_mode="Markdown")