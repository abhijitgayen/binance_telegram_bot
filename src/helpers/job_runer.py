import asyncio
import time
from telegram import Update
from telegram.ext import ContextTypes
from setting import LIST_ADS_SLEEP , CREATE_ORDER_SLEEP

class JobRunner:
    def __init__(self):
        self.stop_threads = False
        self.fetch_task = None
        self.process_task = None

    # Example Job 1: Fetch Ads (with a parameter)
    async def fetch_ads(self, db, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        while not self.stop_threads:
            print(f"Fetching ads from ...")
            await update.message.reply_text("Fetching ads from ...", disable_notification=True)
            await asyncio.sleep(LIST_ADS_SLEEP)   
            if callback:
                callback("Fetched Ads")

    # Example Job 2: Process Ads (with a parameter)
    async def process_ads(self, db, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        while not self.stop_threads:
            print(f"Processing ads with method...")
            await update.message.reply_text('Processing ads with method...', disable_notification=True)
            await asyncio.sleep(CREATE_ORDER_SLEEP)
            if callback:
                callback("Processed Ads")

    # Function to run both jobs in parallel with parameters and callback
    def run_parallel_jobs(self, db, update: Update, context: ContextTypes.DEFAULT_TYPE, callback=None):
        self.stop_threads = False  # Reset stop flag

        # Create and start asyncio tasks for both jobs
        loop = asyncio.get_event_loop()
        self.fetch_task = loop.create_task(self.fetch_ads(db, update, context, callback))
        self.process_task = loop.create_task(self.process_ads(db, update, context, callback))

    # Method to stop the tasks manually
    def stop(self):
        print("Stopping jobs manually...")
        self.stop_threads = True  # Set the flag to stop the jobs

        if self.fetch_task:
            self.fetch_task.cancel()
        if self.process_task:
            self.process_task.cancel()

        print("Jobs have been stopped.")
