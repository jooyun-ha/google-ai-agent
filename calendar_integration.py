"""
Google Calendar API Integration
Fetches and parses calendar events for Lunza agent
"""
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/gmail.send']

class CalendarService:
    """Wrapper for Google Calendar API operations"""
    
    def __init__(self):
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate and create Calendar service"""
        creds = None
        # The file token.json stores the user's access and refresh tokens.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.creds = creds
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_upcoming_events(self, hours_ahead: int = 4, max_results: int = 10) -> List[Dict]:
        """
        Fetch upcoming events from the primary calendar
        
        Args:
            hours_ahead: How many hours ahead to look
            max_results: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(hours=hours_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return [self._parse_event(event) for event in events]
        
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def filter_lunch_meetings(self, events: List[Dict]) -> List[Dict]:
        """
        Filter events to only include lunch meetings
        
        Criteria:
        - Time between 11 AM - 2 PM
        - Contains lunch-related keywords in title/description
        """
        lunch_events = []
        lunch_keywords = ['lunch', 'meal', 'dining', 'restaurant', 'food', 'eat']
        
        for event in events:
            start_time = event.get('start_time')
            if not start_time:
                continue
            
            # Parse time
            try:
                if 'T' in start_time:
                    event_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    hour = event_time.hour
                else:
                    continue
            except:
                continue
            
            # Check time range (11 AM - 2 PM)
            if 11 <= hour <= 14:
                # Check for lunch keywords
                title = event.get('title', '').lower()
                description = event.get('description', '').lower()
                
                if any(keyword in title or keyword in description for keyword in lunch_keywords):
                    lunch_events.append(event)
                elif hour == 12:  # 12 PM is likely lunch
                    lunch_events.append(event)
        
        return lunch_events
    
    def _parse_event(self, event: Dict) -> Dict:
        """Parse Google Calendar event into standardized format"""
        start = event.get('start', {})
        end = event.get('end', {})
        
        return {
            'event_id': event.get('id'),
            'title': event.get('summary', 'No Title'),
            'location': event.get('location', ''),
            'start_time': start.get('dateTime', start.get('date', '')),
            'end_time': end.get('dateTime', end.get('date', '')),
            'description': event.get('description', ''),
            'attendees': [att.get('email') for att in event.get('attendees', [])],
            'organizer': event.get('organizer', {}).get('email', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', '')
        }
    
    def update_event_with_recommendation(self, event_id: str, recommendation: str) -> bool:
        """
        Add recommendation to calendar event description
        
        Args:
            event_id: Calendar event ID
            recommendation: Recommendation text to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            current_description = event.get('description', '')
            new_description = f"{current_description}\n\n---\n🍽️ Lunza Recommendation:\n{recommendation}"
            
            event['description'] = new_description
            
            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            print(f"✅ Updated calendar event: {updated_event.get('summary')}")
            return True
        
        except HttpError as error:
            print(f'❌ Error updating event: {error}')
            return False

