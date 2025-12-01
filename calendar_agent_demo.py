"""
Calendar Agent Demo Mode
Uses mock calendar data so judges can test without real calendar access
"""
import os
import json
from typing import Dict, List
from datetime import datetime, timedelta
from event_processor import EventProcessor
from notification_service import NotificationService
from agent import run_enhanced_lunza

class CalendarAgentDemo:
    """Demo version that uses mock calendar events"""
    
    def __init__(self):
        self.event_processor = EventProcessor('demo_processed_events.json')
        self.notification_service = NotificationService()
    
    def get_mock_calendar_events(self) -> List[Dict]:
        """Generate mock calendar events for demonstration"""
        now = datetime.now()
        
        # Create a lunch meeting for tomorrow at 12:30 PM
        tomorrow = now + timedelta(days=1)
        lunch_time = tomorrow.replace(hour=12, minute=30, second=0, microsecond=0)
        
        mock_events = [
            {
                'event_id': 'demo_lunch_1',
                'title': 'Team Lunch Meeting',
                'location': 'San Francisco, near GitHub HQ',
                'start_time': lunch_time.isoformat(),
                'end_time': (lunch_time + timedelta(hours=1)).isoformat(),
                'description': 'Need healthy lunch options for diabetes management. Looking for low-carb, high-protein options.',
                'attendees': ['alice@example.com', 'bob@example.com'],
                'organizer': 'demo@example.com',
                'created': now.isoformat(),
                'updated': now.isoformat()
            },
            {
                'event_id': 'demo_lunch_2',
                'title': 'Client Lunch',
                'location': 'Downtown San Francisco',
                'start_time': (lunch_time + timedelta(days=1)).isoformat(),
                'end_time': (lunch_time + timedelta(days=1, hours=1)).isoformat(),
                'description': 'Business lunch. Need vegetarian options.',
                'attendees': ['client@example.com'],
                'organizer': 'demo@example.com',
                'created': now.isoformat(),
                'updated': now.isoformat()
            }
        ]
        
        return mock_events
    
    def filter_lunch_meetings(self, events: List[Dict]) -> List[Dict]:
        """Filter events to only include lunch meetings (mock version)"""
        lunch_events = []
        lunch_keywords = ['lunch', 'meal', 'dining', 'restaurant', 'food', 'eat']
        
        for event in events:
            start_time = event.get('start_time')
            if not start_time:
                continue
            
            try:
                event_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                hour = event_time.hour
            except:
                continue
            
            # Check time range (11 AM - 2 PM)
            if 11 <= hour <= 14:
                title = event.get('title', '').lower()
                description = event.get('description', '').lower()
                
                if any(keyword in title or keyword in description for keyword in lunch_keywords):
                    lunch_events.append(event)
                elif hour == 12:  # 12 PM is likely lunch
                    lunch_events.append(event)
        
        return lunch_events
    
    def process_calendar_events(self):
        """Main function: Process mock calendar events"""
        print(f"\n{'='*60}")
        print(f"📅 DEMO MODE: Processing mock calendar events ({self._get_timestamp()})")
        print('='*60)
        print("ℹ️  Using mock calendar data - no real calendar access needed")
        print('='*60)
        
        # Get mock events
        events = self.get_mock_calendar_events()
        print(f"📋 Found {len(events)} mock events")
        
        # Filter for lunch meetings
        lunch_events = self.filter_lunch_meetings(events)
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
            print(f"   ✅ Constraints: {json.dumps(constraints, indent=2)}")
            
            # Build query from constraints
            query = self._build_query_from_constraints(constraints, event)
            print(f"   💬 Query: {query}")
            
            # Run Lunza agent
            print("   🤖 Running Lunza agent...")
            recommendation = self._run_lunza_with_constraints(constraints, query)
            
            if recommendation:
                # Show notification (demo mode - just print)
                print("   📧 Notification (Demo Mode - would send email in production):")
                print("   " + "="*56)
                self._show_demo_notification(recommendation, event, constraints)
                print("   " + "="*56)
                
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
        """Run Lunza agent with pre-extracted constraints"""
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        # Capture both stdout and stderr
        f = io.StringIO()
        try:
            # Temporarily redirect output
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = f
            sys.stderr = f
            
            from agent import run_enhanced_lunza
            run_enhanced_lunza(
                query, 
                skip_prompts=True, 
                pre_extracted_constraints=constraints
            )
            
            # Restore output
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            output = f.getvalue()
            
            # Extract recommendation from output
            if "LUNZA FINAL RECOMMENDATION:" in output:
                parts = output.split("LUNZA FINAL RECOMMENDATION:")
                if len(parts) > 1:
                    recommendation = parts[1].split("="*60)[0].strip()
                    if recommendation:
                        return recommendation
            
            # If no clear recommendation found, return the full output
            return output if output else None
            
        except Exception as e:
            # Restore output on error
            if 'old_stdout' in locals():
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            print(f"   ⚠️  Error running Lunza: {e}")
            return None
    
    def _show_demo_notification(self, recommendation: str, event: Dict, constraints: Dict):
        """Show what notification would look like"""
        print(f"\n   📧 Email would be sent to: {os.getenv('NOTIFICATION_EMAIL', 'user@example.com')}")
        print(f"   📅 Event: {event.get('title')}")
        print(f"   📍 Location: {event.get('location', 'N/A')}")
        print(f"   ⏰ Time: {constraints.get('time', 'N/A')}")
        print(f"\n   {recommendation[:200]}...")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def main():
    """Main entry point for demo mode"""
    print("\n" + "="*60)
    print("🎭 LUNZA CALENDAR AGENT - DEMO MODE")
    print("="*60)
    print("This demo uses mock calendar data.")
    print("No real calendar access or credentials needed!")
    print("="*60)
    
    agent = CalendarAgentDemo()
    agent.process_calendar_events()
    
    print("\n" + "="*60)
    print("✅ Demo completed!")
    print("="*60)
    print("\n💡 For judges:")
    print("   - This demo shows the full calendar integration flow")
    print("   - Uses mock calendar events (no privacy concerns)")
    print("   - Shows how the system extracts constraints and generates recommendations")
    print("   - To test with real calendar: python3 calendar_agent.py --once")
    print("="*60)

if __name__ == "__main__":
    main()

