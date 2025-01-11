# Telegram Bot with Docker Support

This project is a Telegram bot designed for various operations like configuration management, bot control, and user interactions. It uses Python and leverages the `python-telegram-bot` library for seamless integration with the Telegram API.

## Features

- Custom command handlers for bot control and configuration management.
- Reply to user messages with predefined responses.
- Callback query handling for interactive buttons.
- Database integration to store user and bot configurations.
- Job runner for scheduled tasks.

---

## Project Setup

### Prerequisites

Ensure the following are installed on your system:

- Docker
- Python 3.12+
- `pip` (Python package manager)

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/abhijitgayen/binance_telegram_bot.git 
   cd binance_telegram_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with the following content:
   ```dotenv
   BINANCE_API_URL=https://api.binance.com
   TELEGRAM_TOKEN=7908006935:AAE3PQUHwESkWCCplmde1F8l234freferfk
   NOTIFY_USER_ID=2085862908
   ALLOWED_USER=6426250608
   LIST_ADS_SLEEP=5
   CREATE_ORDER_SLEEP=9
   ```

4. Run the bot locally:
   ```bash
   python main.py
   ```

---

### Docker Setup

1. Build the Docker image:
   ```bash
   docker build -t telegram_bot .
   ```

2. Run the Docker container with the `.env` file:
   ```bash
   docker run --env-file .env telegram_bot
   ```

3. Check the logs to ensure the bot is running:
   ```bash
   docker logs <container_id>
   ```