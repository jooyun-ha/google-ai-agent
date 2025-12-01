"""
Scheduler Module
Handles automatic checking and processing of calendar events
"""
import time
import schedule
from typing import Callable, Optional
from datetime import datetime

class Scheduler:
    """Manages scheduled tasks for calendar checking"""
    
    def __init__(self, check_interval_minutes: int = 30):
        self.check_interval_minutes = check_interval_minutes
        self.is_running = False
    
    def schedule_task(self, task_function: Callable):
        """
        Schedule a task to run at regular intervals
        
        Args:
            task_function: Function to call on schedule
        """
        schedule.every(self.check_interval_minutes).minutes.do(task_function)
        print(f"📅 Scheduled task to run every {self.check_interval_minutes} minutes")
    
    def run_once(self, task_function: Callable):
        """Run task once immediately"""
        print("🚀 Running one-time check...")
        task_function()
    
    def run_continuously(self):
        """Run scheduler continuously"""
        self.is_running = True
        print(f"⏰ Scheduler started. Checking every {self.check_interval_minutes} minutes...")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped.")
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False

