# Lunza Architecture: Google Calendar Integration

## Current Architecture (Manual Mode)

```
User Input → Planner Agent → Maps Tool → Health Scoring → Session Memory → Final Agent → Output
```

## Proposed Architecture (Calendar-Integrated Mode)

### Option 1: Scheduled Check Mode (Recommended for MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCHEDULER / CRON JOB                         │
│              (Runs every 15-30 minutes)                          │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE CALENDAR API INTEGRATION                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Fetch upcoming events (next 2-4 hours)                │  │
│  │ 2. Filter for lunch meetings (11 AM - 2 PM)             │  │
│  │ 3. Extract: title, location, time, attendees, notes      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              EVENT PROCESSOR                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Check if event already processed (avoid duplicates)    │  │
│  │ • Extract meeting constraints from event                 │  │
│  │ • Determine if lunch recommendation needed               │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              EXISTING LUNZA PIPELINE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Planner  │→ │   Maps   │→ │  Health  │→ │  Final   │      │
│  │  Agent   │  │   Tool   │  │ Scoring  │  │  Agent   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              NOTIFICATION SYSTEM                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Email (Gmail API)                                       │  │
│  │ • Calendar Event Update (add recommendation as note)     │  │
│  │ • Slack/Teams Webhook (optional)                         │  │
│  │ • SMS (Twilio, optional)                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Option 2: Webhook Mode (Advanced)

```
Google Calendar Webhook → Event Trigger → Process Event → Lunza Pipeline → Notification
```

## Component Breakdown

### 1. Google Calendar API Integration

**Purpose:** Fetch and parse calendar events

**Components:**
- `CalendarService` class
  - `get_upcoming_events(hours_ahead=4)` - Get events in next N hours
  - `filter_lunch_meetings(events)` - Filter 11 AM - 2 PM events
  - `extract_event_details(event)` - Parse event data
  - `is_lunch_meeting(event)` - Check if event is lunch-related

**Data Extracted:**
```python
{
    "event_id": "abc123",
    "title": "Team Lunch",
    "location": "San Francisco, near GitHub HQ",
    "start_time": "2024-01-15T12:30:00",
    "end_time": "2024-01-15T13:30:00",
    "attendees": ["alice@example.com", "bob@example.com"],
    "description": "Need healthy options for diabetes",
    "organizer": "user@example.com"
}
```

### 2. Event Processor

**Purpose:** Transform calendar events into Lunza constraints

**Components:**
- `EventProcessor` class
  - `process_event(event)` - Main processing function
  - `extract_constraints(event)` - Convert event → constraints
  - `check_if_processed(event_id)` - Avoid duplicate processing
  - `mark_as_processed(event_id)` - Track processed events

**Transformation:**
```python
Calendar Event → Lunza Constraints
{
    "area": event.location or "San Francisco",
    "venue": extract_venue(event.location),
    "time": event.start_time,
    "diet": extract_from_description(event.description),
    "health": extract_health_notes(event.description)
}
```

### 3. Scheduler / Trigger System

**Option A: Python Scheduler (Simple)**
```python
# Using schedule library
import schedule
import time

def check_calendar_and_recommend():
    events = calendar_service.get_upcoming_events()
    for event in events:
        if should_process(event):
            run_lunza_for_event(event)

schedule.every(30).minutes.do(check_calendar_and_recommend)
```

**Option B: Cron Job**
```bash
# Run every 30 minutes
*/30 * * * * /usr/bin/python3 /path/to/calendar_agent.py
```

**Option C: Google Cloud Functions / AWS Lambda**
- Serverless, triggered by Cloud Scheduler
- Better for production

### 4. Notification System

**Components:**
- `NotificationService` class
  - `send_email(recommendation, event)` - Email via Gmail API
  - `update_calendar_event(event_id, recommendation)` - Add to event notes
  - `send_slack_message(recommendation)` - Slack webhook (optional)

**Output Format:**
```
Subject: Lunch Recommendation for [Event Title]

Hi! Here's your lunch recommendation for today's meeting:

[Top 3 restaurants with addresses and menu suggestions]

---
Generated by Lunza AI Agent
```

## Data Flow Example

### Scenario: User has "Team Lunch" event at 12:30 PM

1. **Scheduler triggers** (every 30 min)
2. **Calendar API** fetches events:
   ```json
   {
     "title": "Team Lunch",
     "location": "San Francisco, near GitHub HQ",
     "start": "2024-01-15T12:30:00",
     "description": "Need healthy options for diabetes"
   }
   ```

3. **Event Processor** extracts constraints:
   ```json
   {
     "area": "San Francisco",
     "venue": "GitHub HQ",
     "time": "12:30 PM",
     "diet": "diabetes",
     "health": null
   }
   ```

4. **Lunza Pipeline** runs:
   - Planner Agent: Already has constraints (skip)
   - Maps Tool: Searches restaurants near GitHub HQ
   - Health Scoring: Ranks for diabetes-friendly
   - Final Agent: Generates top 3 recommendations

5. **Notification** sent:
   - Email to user
   - Calendar event updated with recommendation

## File Structure

```
google-ai-agent/
├── agent.py                    # Current Lunza agent (core logic)
├── calendar_integration.py     # NEW: Calendar API wrapper
├── event_processor.py           # NEW: Event → Constraints converter
├── scheduler.py                # NEW: Scheduling logic
├── notification_service.py      # NEW: Email/Calendar notifications
├── calendar_agent.py           # NEW: Main entry point for calendar mode
├── config.py                   # NEW: Configuration settings
└── requirements.txt            # Updated with calendar dependencies
```

## API Requirements

### Google APIs Needed:

1. **Google Calendar API**
   - Read calendar events
   - Update events (add recommendations)
   - OAuth 2.0 authentication

2. **Gmail API** (for email notifications)
   - Send emails
   - OAuth 2.0 authentication

3. **Google Places API** (already planned)
   - Search restaurants
   - Get restaurant details

### Authentication Flow:

```
User → OAuth Consent Screen → Authorization Code → Access Token → API Calls
```

**Storage:**
- `token.json` - OAuth tokens (gitignored)
- `credentials.json` - OAuth client credentials (gitignored)

## Configuration

### `.env` additions:
```env
# Existing
GOOGLE_API_KEY=your_gemini_key
GOOGLE_PLACES_API_KEY=your_places_key

# New for Calendar
GOOGLE_CALENDAR_CLIENT_ID=your_client_id
GOOGLE_CALENDAR_CLIENT_SECRET=your_client_secret
GOOGLE_CALENDAR_REDIRECT_URI=http://localhost:8080/callback

# Notification settings
NOTIFICATION_EMAIL=your_email@gmail.com
NOTIFICATION_METHOD=email  # email, calendar, slack, sms
CHECK_INTERVAL_MINUTES=30
```

## Execution Modes

### Mode 1: Manual (Current)
```bash
python3 agent.py
# User types query manually
```

### Mode 2: Calendar-Automated
```bash
python3 calendar_agent.py
# Runs continuously, checks calendar every 30 min
```

### Mode 3: One-time Check
```bash
python3 calendar_agent.py --once
# Check calendar once and exit
```

## Implementation Phases

### Phase 1: Basic Calendar Integration
- [ ] Google Calendar API setup
- [ ] Fetch upcoming events
- [ ] Extract event details
- [ ] Connect to existing Lunza pipeline

### Phase 2: Automation
- [ ] Scheduler implementation
- [ ] Duplicate event detection
- [ ] Event filtering (lunch meetings only)

### Phase 3: Notifications
- [ ] Email notifications
- [ ] Calendar event updates
- [ ] Error handling

### Phase 4: Advanced Features
- [ ] Webhook support
- [ ] Multi-calendar support
- [ ] User preferences
- [ ] Analytics/logging

## Security Considerations

1. **OAuth Tokens**: Store securely, never commit
2. **API Keys**: Use environment variables
3. **Rate Limiting**: Respect API quotas
4. **Error Handling**: Graceful failures
5. **Logging**: Track without exposing sensitive data

## Dependencies to Add

```txt
google-api-python-client>=2.100.0  # Calendar & Gmail APIs
google-auth-httplib2>=0.1.1       # HTTP transport
google-auth-oauthlib>=1.1.0        # OAuth flow
schedule>=1.2.0                    # Task scheduling
```

## Questions to Consider

1. **When to trigger?**
   - How far in advance? (2 hours? 4 hours?)
   - What time range counts as "lunch"? (11 AM - 2 PM?)

2. **How to identify lunch meetings?**
   - Keyword matching ("lunch", "meal", "dining")?
   - Time-based (11 AM - 2 PM)?
   - User tagging?

3. **Notification preferences?**
   - Email only?
   - Add to calendar event?
   - Multiple channels?

4. **Error handling?**
   - What if calendar API fails?
   - What if no restaurants found?
   - Retry logic?

5. **User experience?**
   - Opt-in/opt-out per event?
   - Preferences per user?
   - Feedback mechanism?

