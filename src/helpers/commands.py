from telegram import Update
from telegram.ext import ContextTypes
from src.helpers.auth import restricted
from src.db.init import Database
from src.helpers.generate_message import generate_config_message
from setting import DEFAULT_BOT_CONFIG
from src.helpers.job_runer import JobRunner
from datetime import datetime


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    db: Database = context.application.db
    user = update.effective_user
    db.insert_user(user_id = user.id, first_name= user.first_name, last_name = user.last_name, extra_info = DEFAULT_BOT_CONFIG)
    await update.message.reply_text("🤖 Welcome aboard! \nI'm your Binance C2C bot, \nhere to make trading smooth and easy. 🚀\nType /help to explore my features and get started! 🛠️\n\n🔒 (Access restricted to authorized users)")

@restricted
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_runner: JobRunner = context.application.job_runner
    job_runner.stop()
    stop_reply = f"🚫 All background tasks have been stopped!\n You can check status using /status.\n⬅ Ready to roll again? \nUse /run to get the bot back in action! 🚀"
    await update.message.reply_text(stop_reply, parse_mode="Markdown")

@restricted
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_runner: JobRunner = context.application.job_runner
    db: Database = context.application.db
    user_data = db.get_user(update.effective_user.id)
    
    if (not user_data) or (not user_data.get('bot_config')):
        await need_to_start (update)
        return

    bot_config = user_data.get('bot_config') or {}
    job_runner.set_api_config(bot_config)
    run_reply = f"🤖 The bot is running in the background!\n\n✨ To stop it, use: /stop\n🔍 To check its status, use: /status"
    await update.message.reply_text(run_reply, parse_mode="Markdown")

    job_runner.run_parallel_jobs(db, update, context)

@restricted
async def clean_ads (update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db: Database = context.application.db
    db.delete_all_ads()
    clean_ads_reply = "🚨 **ALL ADS CLEARED!** 🚨\n\n All ads have been successfully deleted from the system."
    await update.message.reply_text(clean_ads_reply, parse_mode="Markdown")
    

@restricted
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    job_runner: JobRunner = context.application.job_runner
    bot_status = job_runner.runner_status()

    if bot_status.get("running") and bot_status.get('job1') and bot_status.get('job2') :
        current_time = datetime.now()
        job1_last_time = (current_time - bot_status['job1']).total_seconds() if bot_status.get('job1') else None
        job2_last_time = (current_time - bot_status['job2']).total_seconds() if bot_status.get('job2') else None
        message = f"✅ The bot is up and running! 🚀\n\n🔹 Job 1: Completed {job1_last_time} seconds ago.\n🔹 Job 2: Completed {job2_last_time} seconds ago.\n\nSit back and let the bot handle the tasks! 💼"
    else:
        message = "🚨 Heads up! 🚨\n\nThe bot is currently taking a break \nand not running any background jobs. \nNeed to kick it back into action? \nUse the /run command! ⚡"

    await update.message.reply_text(message, parse_mode="Markdown")

@restricted
async def get_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /get_config command to view the current configuration."""
    db: Database = context.application.db
    user_data = db.get_user(update.effective_user.id)

    if (not user_data) or (not user_data.get('bot_config')):
        await need_to_start (update)
        return

    bot_config = user_data.get('bot_config') or {}
    config_message = generate_config_message (bot_config)
    await update.message.reply_text(config_message, parse_mode="Markdown")
    await update.message.reply_text("use /set_config to set the config of bot")

@restricted
async def set_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /set_config command."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "🛠 **Usage:**\n"
            "`/set_config <key> <value>`\n\n"
            "📌 **Example:**\n"
            "`/set_config TRADE_TYPE SELL`\n\n"
            "🔗 **For arrays:**\n"
            "`/set_config EXTRA_FILTER.error_codes 83683,83682`",
            parse_mode="Markdown"
        )

        return

    key = context.args[0]
    value = ' '.join(context.args[1:])  # Join all remaining args

    # Handle array values
    if key == "EXTRA_FILTER.error_codes":
        try:
            # Remove brackets and split by comma
            value = value.strip('[]').replace(' ', '').split(',')
            # Remove empty strings
            value = [v.strip("'\"") for v in value if v]
        except:
            await update.message.reply_text("❌ Invalid array format. Use: `83683,83682`", parse_mode="Markdown")
            return
    else:
        # Convert value to int or float if needed
        try:
            if value.isdigit():
                value = int(value)
            else:
                value = float(value) if '.' in value else value
        except ValueError:
            pass

    user_id = update.effective_user.id
    db: Database = context.application.db

    success = await update_config(user_id, key, value, db, update)
    if success:
        await update.message.reply_text(f"✅ Updated >> {key} : {value} \n\n To see the config run /get_config")
    else:
        await update.message.reply_text(f"❌ Failed to update configuration. Invalid key: `{key}`", parse_mode="Markdown")

async def update_config(user_id, key, value, db: Database, update: Update) -> bool:
    user_data = db.get_user(user_id)

    if (not user_data) or (not user_data.get('bot_config')):
        await need_to_start (update)
        return

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
        db.update_bot_config(user_id, current_config)
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
        "/clean_ads - Used to clean all ads\n"
        "/status - check status of the jobs\n"
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

async def need_to_start (update: Update) -> None:
    need_start_message = "🚀 To get started, please start the chatbot \nand complete the initial configuration setup.\nLet's get everything ready for a smooth experience! 😊\nUse the command /start to start the bot."
    await update.message.reply_text(need_start_message, parse_mode="Markdown")
