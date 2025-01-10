import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes
from setting import LIST_ADS_SLEEP , CREATE_ORDER_SLEEP, BINANCE_API_URL
from src.apis.binance_api_call import BinanceApiCall
from src.db.init import Database
from datetime import datetime


class JobRunner:
    def __init__(self):
        self.stop_threads = False
        self.fetch_task = None
        self.process_task = None
        self.binance_api = BinanceApiCall(base_url=BINANCE_API_URL)
        self.job_status = {}

    def runner_status (self):
        return {**self.job_status, **{"running": not self.stop_threads}}

    # Job 1: Fetch Ads
    async def fetch_ads(self, db: Database, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        while not self.stop_threads:
            try:
                self.job_status = {**self.job_status,**{"job1": datetime.now()}}
                ads = self.binance_api.search_ads_jobs()
                if ads.get("error_code"):
                    error_message = f"🛑 ERROR IN LIST ADS 🛑\n\nCODE: {ads.get('error_code')}\nMSG: {ads.get('error_message')}\n\n🙏 Plz stop the bot if you want /stop "
                    await update.message.reply_text(error_message, parse_mode="Markdown")
                else:
                    db.insert_ad(ads.get("data") or [])
            except Exception as e:
                print(f"An error occurred while creating order jobs: {e}")

            await asyncio.sleep(LIST_ADS_SLEEP)  
            

    # Job 2: Process Ads
    async def process_ads(self, db: Database, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        while not self.stop_threads:
            self.job_status = {**self.job_status,**{"job2": datetime.now()}}
            try:
                await self.binance_api.create_orders_jobs(db,update)
            except Exception as e:
                print(f"An error occurred while creating order jobs: {e}")
            # await update.message.reply_text('Processing ads with method...', disable_notification=True)
            await asyncio.sleep(CREATE_ORDER_SLEEP)

    # Function to run both jobs in parallel with parameters and callback
    def run_parallel_jobs(self, db, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        self.stop_threads = False  # Reset stop flag

        # Create and start asyncio tasks for both jobs
        loop = asyncio.get_event_loop()
        self.fetch_task = loop.create_task(self.fetch_ads(db, update, context, callback))
        self.process_task = loop.create_task(self.process_ads(db, update, context, callback))

    def set_api_config(self, config):
        self.binance_api.set_config(config)

    # Method to stop the tasks manually
    def stop(self):
        print("Stopping jobs manually...")
        self.stop_threads = True  # Set the flag to stop the jobs

        if self.fetch_task:
            self.fetch_task.cancel()
        if self.process_task:
            self.process_task.cancel()

        print("Jobs have been stopped.")
