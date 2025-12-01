"""
Event Processor
Converts calendar events into Lunza constraints and manages processed events
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class EventProcessor:
    """Processes calendar events and converts them to Lunza constraints"""
    
    def __init__(self, processed_events_file: str = 'processed_events.json'):
        self.processed_events_file = processed_events_file
        self.processed_events = self._load_processed_events()
    
    def _load_processed_events(self) -> set:
        """Load list of already processed event IDs"""
        if os.path.exists(self.processed_events_file):
            try:
                with open(self.processed_events_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('event_ids', []))
            except:
                return set()
        return set()
    
    def _save_processed_events(self):
        """Save processed event IDs to file"""
        with open(self.processed_events_file, 'w') as f:
            json.dump({'event_ids': list(self.processed_events)}, f, indent=2)
    
    def check_if_processed(self, event_id: str) -> bool:
        """Check if event has already been processed"""
        return event_id in self.processed_events
    
    def mark_as_processed(self, event_id: str):
        """Mark event as processed"""
        self.processed_events.add(event_id)
        self._save_processed_events()
    
    def extract_constraints(self, event: Dict) -> Dict:
        """
        Extract Lunza constraints from calendar event
        
        Args:
            event: Calendar event dictionary
            
        Returns:
            Constraints dictionary with: area, venue, time, diet, health
        """
        constraints = {
            "area": None,
            "venue": None,
            "time": None,
            "diet": None,
            "health": None
        }
        
        # Extract area/venue from location
        location = event.get('location', '')
        if location:
            constraints["area"] = self._extract_area(location)
            constraints["venue"] = self._extract_venue(location)
        
        # Extract time
        start_time = event.get('start_time', '')
        if start_time:
            constraints["time"] = self._format_time(start_time)
        
        # Extract diet and health from description
        description = event.get('description', '')
        title = event.get('title', '')
        full_text = f"{title} {description}".lower()
        
        constraints["diet"] = self._extract_diet(full_text)
        constraints["health"] = self._extract_health(full_text)
        
        # Default area if not found
        if not constraints["area"]:
            constraints["area"] = "San Francisco"
        
        return constraints
    
    def _extract_area(self, location: str) -> Optional[str]:
        """Extract general area from location string"""
        # Common area patterns
        areas = ['san francisco', 'sf', 'downtown', 'soma', 'mission', 
                 'financial district', 'north beach', 'hayes valley']
        
        location_lower = location.lower()
        for area in areas:
            if area in location_lower:
                return area.title()
        
        # If contains city name, return it
        if 'san francisco' in location_lower or 'sf' in location_lower:
            return "San Francisco"
        
        return None
    
    def _extract_venue(self, location: str) -> Optional[str]:
        """Extract specific venue from location string"""
        # Look for common venue indicators
        venue_keywords = ['near', 'at', '@', 'hq', 'headquarters', 'office']
        
        location_lower = location.lower()
        for keyword in venue_keywords:
            if keyword in location_lower:
                # Extract text after keyword
                parts = location_lower.split(keyword, 1)
                if len(parts) > 1:
                    venue = parts[1].strip()
                    # Clean up common suffixes
                    for suffix in [',', '.', 'san francisco', 'sf', 'ca']:
                        venue = venue.replace(suffix, '').strip()
                    if venue:
                        return venue.title()
        
        return None
    
    def _format_time(self, time_str: str) -> Optional[str]:
        """Format ISO time string to readable format"""
        try:
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.strftime('%I:%M %p')
        except:
            pass
        return None
    
    def _extract_diet(self, text: str) -> Optional[str]:
        """Extract dietary restrictions from text"""
        diet_keywords = {
            'diabetes': ['diabetes', 'diabetic', 'blood sugar'],
            'vegetarian': ['vegetarian', 'veggie'],
            'vegan': ['vegan'],
            'keto': ['keto', 'ketogenic'],
            'gluten-free': ['gluten-free', 'gluten free', 'celiac'],
            'low-carb': ['low carb', 'low-carb', 'low carb'],
            'paleo': ['paleo']
        }
        
        for diet, keywords in diet_keywords.items():
            if any(keyword in text for keyword in keywords):
                return diet
        
        return None
    
    def _extract_health(self, text: str) -> Optional[str]:
        """Extract health considerations from text"""
        health_keywords = {
            'low carb': ['low carb', 'low-carb'],
            'high protein': ['high protein', 'protein'],
            'brain fuel': ['brain', 'focus', 'energy'],
            'healthy': ['healthy', 'nutritious']
        }
        
        for health, keywords in health_keywords.items():
            if any(keyword in text for keyword in keywords):
                return health
        
        return None
    
    def should_process_event(self, event: Dict) -> bool:
        """
        Determine if event should be processed
        
        Returns True if:
        - Not already processed
        - Has valid time
        - Appears to be a lunch meeting
        """
        event_id = event.get('event_id')
        
        # Check if already processed
        if event_id and self.check_if_processed(event_id):
            return False
        
        # Check if has valid time
        if not event.get('start_time'):
            return False
        
        return True

