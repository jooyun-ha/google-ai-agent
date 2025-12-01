"""
Calendar Agent - Main Entry Point
Automatically processes calendar events and generates lunch recommendations
"""
import os
import sys
import argparse
from typing import Dict
from calendar_integration import CalendarService
from event_processor import EventProcessor
from notification_service import NotificationService
from scheduler import Scheduler
from agent import run_enhanced_lunza
from dotenv import load_dotenv

load_dotenv()

class CalendarAgent:
    """Main agent that processes calendar events automatically"""
    
    def __init__(self):
        self.calendar_service = CalendarService()
        self.event_processor = EventProcessor()
        self.notification_service = NotificationService()
        self.check_interval = int(os.getenv('CHECK_INTERVAL_MINUTES', 30))
    
    def process_calendar_events(self):
        """Main function: Check calendar and process events"""
        print(f"\n{'='*60}")
        print(f"📅 Checking calendar events... ({self._get_timestamp()})")
        print('='*60)
        
        # Fetch upcoming events (check next 24 hours to catch tomorrow's lunch meetings)
        events = self.calendar_service.get_upcoming_events(hours_ahead=24)
        print(f"📋 Found {len(events)} upcoming events")
        
        # Filter for lunch meetings
        lunch_events = self.calendar_service.filter_lunch_meetings(events)
        print(f"🍽️  Found {len(lunch_events)} lunch meetings")
        
        if not lunch_events:
            print("✅ No lunch meetings found. Nothing to process.")
            return
        
        # Process each lunch event
        for event in lunch_events:
            self._process_event(event)
    
    def _process_event(self, event: Dict):
        """Process a single calendar event"""
        event_id = event.get('event_id')
        event_title = event.get('title', 'Unknown')
        
        print(f"\n📌 Processing: {event_title}")
        
        # Check if already processed
        if self.event_processor.check_if_processed(event_id):
            print(f"   ⏭️  Already processed, skipping...")
            return
        
        # Check if should process
        if not self.event_processor.should_process_event(event):
            print(f"   ⏭️  Skipping event (invalid or not a lunch meeting)")
            return
        
        try:
            # Extract constraints from event
            print("   🔍 Extracting constraints...")
            constraints = self.event_processor.extract_constraints(event)
            print(f"   ✅ Constraints: {constraints}")
            
            # Build query from constraints
            query = self._build_query_from_constraints(constraints, event)
            print(f"   💬 Query: {query}")
            
            # Run Lunza agent (we'll need to modify run_enhanced_lunza to accept constraints)
            print("   🤖 Running Lunza agent...")
            recommendation = self._run_lunza_with_constraints(constraints, query)
            
            if recommendation:
                # Send notifications
                print("   📧 Sending notifications...")
                self.notification_service.send_recommendation(
                    recommendation, event, constraints
                )
                
                # Update calendar event
                self.calendar_service.update_event_with_recommendation(
                    event_id, recommendation
                )
                
                # Mark as processed
                self.event_processor.mark_as_processed(event_id)
                print(f"   ✅ Successfully processed: {event_title}")
            else:
                print(f"   ❌ Failed to generate recommendation")
        
        except Exception as e:
            print(f"   ❌ Error processing event: {e}")
            import traceback
            traceback.print_exc()
    
    def _build_query_from_constraints(self, constraints: Dict, event: Dict) -> str:
        """Build a natural language query from constraints"""
        parts = []
        
        if constraints.get('area'):
            parts.append(f"in {constraints['area']}")
        
        if constraints.get('venue'):
            parts.append(f"near {constraints['venue']}")
        
        if constraints.get('diet'):
            parts.append(f"that helps with {constraints['diet']}")
        
        if constraints.get('health'):
            parts.append(f"with {constraints['health']} options")
        
        if constraints.get('time'):
            parts.append(f"for my {constraints['time']} meeting")
        
        query = "I want to have lunch " + " ".join(parts)
        return query
    
    def _run_lunza_with_constraints(self, constraints: Dict, query: str) -> str:
        """
        Run Lunza agent with pre-extracted constraints
        Returns the recommendation text
        """
        import io
        from contextlib import redirect_stdout
        
        # Capture output
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                # Run with skip_prompts=True and pre_extracted_constraints
                run_enhanced_lunza(
                    query, 
                    skip_prompts=True, 
                    pre_extracted_constraints=constraints
                )
            
            output = f.getvalue()
            # Extract recommendation from output
            # The recommendation is between "LUNZA FINAL RECOMMENDATION:" and "="*60
            if "LUNZA FINAL RECOMMENDATION:" in output:
                parts = output.split("LUNZA FINAL RECOMMENDATION:")
                if len(parts) > 1:
                    recommendation = parts[1].split("="*60)[0].strip()
                    return recommendation
            
            return output
        except Exception as e:
            print(f"Error running Lunza: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Lunza Calendar Agent')
    parser.add_argument('--once', action='store_true', 
                       help='Run once and exit (don\'t schedule)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in minutes (default: 30)')
    
    args = parser.parse_args()
    
    agent = CalendarAgent()
    
    if args.once:
        # Run once
        agent.process_calendar_events()
    else:
        # Schedule and run continuously
        scheduler = Scheduler(check_interval_minutes=args.interval)
        scheduler.schedule_task(agent.process_calendar_events)
        
        # Run first check immediately
        agent.process_calendar_events()
        
        # Then run on schedule
        scheduler.run_continuously()

if __name__ == "__main__":
    main()

