from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from src.helpers.commands import start, help, about, stop, get_config, set_config, reset, run, status, clean_ads
from setting import TELEGRAM_TOKEN
from src.helpers.send_message import send_text_with_custom_keyboard
from src.db.init import Database
from setting import ALLOWED_USER
from src.helpers.job_runer import JobRunner
from src.helpers.auth import restricted
from src.helpers.notify import notify_admin
from src.helpers.logger import logger
import sys

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    # Notify admin about the error
    await notify_admin(
        context=context,
        error_type="Bot Error",
        details=f"An error occurred: {str(context.error)}",
        update_id=update.update_id if update else None
    )

    if update:
        await update.message.reply_text(
            "Sorry, something went wrong. The administrator has been notified."
        )

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
    try:
        application = Application.builder().token(token).build()
        application.db = Database(f"{ALLOWED_USER}_ops.db")
        application.job_runner = JobRunner()

        # Add error handler
        application.add_error_handler(error_handler)

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
        logger.info("Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if hasattr(application, 'db'):
            application.db.close()
        if hasattr(application, 'job_runner'):
            application.job_runner.stop()

if __name__ == "__main__":
    try:
        if not TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is missing")
        main(token=TELEGRAM_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
