import threading
import time
import sys
from src.db.init import Database
from telegram import Update
from telegram.ext import ContextTypes
import asyncio

class JobRunner:
    def __init__(self):
        self.stop_threads = False
        self.fetch_thread = None
        self.process_thread = None

    # Example Job 1: Fetch Ads (with a parameter)
    def fetch_ads(self, db:Database , update: Update, context: ContextTypes.DEFAULT_TYPE):
        while not self.stop_threads:
            print(f"Fetching ads from ...")
            await update.message.reply_text("Fetching ads from ...", disable_notification=True)
            time.sleep(2)  # Simulate work by waiting for 2 seconds

    # Example Job 2: Process Ads (with a parameter)
    def process_ads(self, db:Database , update: Update, context: ContextTypes.DEFAULT_TYPE):
        while not self.stop_threads:
            print(f"Processing ads with method...")
            await update.message.reply_text('Processing ads with method...', disable_notification=True)
            time.sleep(3)  # Simulate work by waiting for 3 seconds

    # Function to run both jobs in parallel with parameters
    def run_parallel_jobs(self, db:Database , update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Reset stop flag and create threads for both jobs
        self.stop_threads = False
        self.fetch_thread = threading.Thread(target=self.fetch_ads, args=(db, update, context))
        self.process_thread = threading.Thread(target=self.process_ads, args=(db, update, context))

        # Start both threads
        self.fetch_thread.start()
        self.process_thread.start()

    # Method to stop the threads manually
    def stop(self):
        print("Stopping threads manually...")
        self.stop_threads = True  # Set the flag to stop the threads

        if self.fetch_thread and self.fetch_thread.is_alive():
            self.fetch_thread.join()

        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join()

        print("Threads have been stopped.")

# Usage Example
if __name__ == "__main__":
    job_runner = JobRunner()

    # Start the parallel jobs with parameters
    job_runner.run_parallel_jobs(ad_source="API", process_type="Batch")

    # Simulate some running time
    time.sleep(10)  # Run for 10 seconds

    # Stop the threads manually
    job_runner.stop()

    # Restart the parallel jobs with new parameters
    print("\nRestarting jobs with new parameters...\n")
    job_runner.run_parallel_jobs(ad_source="Database", process_type="Real-time")

    # Simulate some more running time
    time.sleep(5)

    # Stop the threads again
    job_runner.stop()

    # Optionally, terminate the program cleanly
    sys.exit(0)
