from telegram import Update
from telegram.ext import ContextTypes
from src.helpers.auth import restricted
from src.db.init import Database
from src.helpers.send_message import send_dynamic_message
from src.helpers.generate_message import generate_config_message
from setting import DEFAULT_BOT_CONFIG
from src.helpers.job_runer import JobRunner


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    db: Database = context.application.db
    user = update.effective_user
    db.insert_user(user_id = user.id, first_name= user.first_name, last_name = user.last_name, extra_info = DEFAULT_BOT_CONFIG)
    await update.message.reply_text("Welcome! I'm your Binance C2C bot. Use /help to see what I can do.")

@restricted
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_runner: JobRunner = context.application.job_runner
    print('it is called')
    job_runner.stop()
    await update.message.reply_text("Bot is stopped")

@restricted
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_runner: JobRunner = context.application.job_runner
    db: Database = context.application.db
    job_runner.run_parallel_jobs(db, update, context)
    await update.message.reply_text('Bot will Run soon')

@restricted
async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /get_config command to view the current configuration."""
    db: Database = context.application.db
    user_data = db.get_user(update.effective_user.id)
    bot_config = user_data.get('bot_config') or {}
    config_message = generate_config_message (bot_config)
    await update.message.reply_text(config_message, parse_mode="Markdown")
    await update.message.reply_text("use /set_config to set the config of bot")

@restricted
async def set_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /set_config command."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: `/set_config <key> <value>` \nExample: `/set_config TRADE_TYPE SELL`",
            parse_mode="Markdown"
        )
        return

    key = context.args[0]
    value = context.args[1]

    # Convert value to int or float if needed
    try:
        if value.isdigit():
            value = int(value)
        else:
            value = float(value) if '.' in value else value
    except ValueError:
        pass  # Leave as a string if it cannot be converted

    user_id = update.effective_user.id
    db_instance :Database = context.application.db

    success = update_config(user_id, key, value, db_instance)
    if success:
        await update.message.reply_text(f"✅ Updated >> {key} : {value} \n\n To see the config run /get_config")
    else:
        await update.message.reply_text(f"❌ Failed to update configuration. Invalid key: `{key}`", parse_mode="Markdown")

def update_config(user_id, key, value, db_instance):
    user_data = db_instance.get_user(user_id)
    current_config = user_data.get('bot_config')

    if not current_config:
        return False  # User or config not found

    # Parse nested keys
    keys = key.split('.')  # For nested keys like EXTRA_FILTER.price
    config_section = current_config

    # Traverse to the nested dictionary
    for k in keys[:-1]:
        if k in config_section:
            config_section = config_section[k]
        else:
            return False  # Invalid key path

    # Update the last key
    last_key = keys[-1]
    if last_key in config_section:
        config_section[last_key] = value
        # Update the database with the new configuration
        db_instance.update_bot_config(user_id, current_config)
        return True

    return False  # Key not found

@restricted
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /reset command."""
    db: Database = context.application.db
    user = update.effective_user
    db.insert_or_update_user(user_id = user.id, first_name= user.first_name, last_name = user.last_name, extra_info = DEFAULT_BOT_CONFIG)
    await update.message.reply_text(
        "Your bot has been reset to the initial bot configuration.\n"
        "/get_config - Get Bot config\n"
        "/set_config - Set Bot config\n"
    )





@restricted
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Here are some commands you can use:\n\n"
        "\n Bot Control\n\n"
        "/start - Start the bot\n"
        "/run - Run the bot\n"
        "/stop - Stop the bot\n"
        "\n Config \n\n"
        "/get_config - Get Bot config\n"
        "/set_config - Set Bot config\n"
        "/reset - Reset the bot config\n"
        "\n Others\n\n"
        "/help - Get help\n"
        "/about - Learn more about this bot"
    )

@restricted
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("A secure bot for seamless peer-to-peer trading on Binance, allowing authorized users to easily execute buy and sell orders.")
