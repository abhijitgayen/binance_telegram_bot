from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.helpers.commands import start, help, about, stop, get_config, set_config, reset, run, status, clean_ads
from setting import TELEGRAM_TOKEN
from src.helpers.send_message import send_text_with_custom_keyboard
from src.db.init import Database
from setting import ALLOWED_USER
from src.helpers.job_runer import JobRunner
from src.helpers.auth import restricted

# Callback Query Handler to process button presses
@restricted
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Get the callback data (the value passed in callback_data)
    callback_data = query.data
    if callback_data == "button_1":
        await query.edit_message_text("You pressed Button 1!")

@restricted
async def reply_hi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! How can I help you today? \nFor assistance, type /help.")


# Main Function to Start the Bot
def main(token):
    application = Application.builder().token(token).build()
    application.db =  Database(f"{ALLOWED_USER}_ops.db")
    application.job_runner = JobRunner()

    # Register command handlers

    # config command
    application.add_handler(CommandHandler("get_config", get_config))
    application.add_handler(CommandHandler("set_config", set_config))
    application.add_handler(CommandHandler("reset", reset))

    # bot control
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("run", run))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("clean_ads",clean_ads))

    # Others
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("about", about))
    

    # Register the message handler to respond 
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_hi))
    # Register the callback query handler to handle button presses
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start the bot
    print("Bot is starting...")
    application.run_polling()
    application.db.close()

if __name__ == "__main__":
    if TELEGRAM_TOKEN is None:
        print("TELEGRAM_TOKEN is missing")
    else:
        main(token=TELEGRAM_TOKEN)
        
