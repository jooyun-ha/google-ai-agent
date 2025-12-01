# Calendar Integration Setup Guide

## Overview

This branch adds Google Calendar integration to Lunza, allowing automatic lunch recommendations based on your calendar events.

## Architecture

See `ARCHITECTURE.md` for detailed architecture documentation.

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Calendar API
   - Gmail API (for email notifications)

### 3. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Desktop app** as application type
4. Download the credentials JSON file
5. Rename it to `credentials.json` and place it in the project root

### 4. Configure Environment Variables

Add to your `.env` file:

```env
# Existing
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_PLACES_API_KEY=your_places_api_key

# Calendar Integration
NOTIFICATION_EMAIL=your_email@gmail.com
NOTIFICATION_METHOD=email  # or 'calendar' for calendar updates only
CHECK_INTERVAL_MINUTES=30
```

### 5. First Run - Authentication

On first run, the script will:
1. Open a browser window for Google OAuth
2. Ask you to sign in and grant permissions
3. Save tokens to `token.json` (automatically created)

```bash
python3 calendar_agent.py --once
```

## Usage

### Run Once (Test)

```bash
python3 calendar_agent.py --once
```

### Run Continuously (Production)

```bash
python3 calendar_agent.py
```

This will:
- Check calendar every 30 minutes (configurable)
- Process lunch meetings automatically
- Send recommendations via email/calendar

### Custom Interval

```bash
python3 calendar_agent.py --interval 15
```

## How It Works

1. **Scheduler** checks calendar every N minutes
2. **Calendar API** fetches upcoming events (next 4 hours)
3. **Event Filter** identifies lunch meetings (11 AM - 2 PM)
4. **Event Processor** extracts constraints from events
5. **Lunza Agent** generates recommendations
6. **Notifications** sent via email and calendar updates

## File Structure

```
calendar-integration/
├── agent.py                    # Core Lunza agent (unchanged)
├── calendar_integration.py     # Google Calendar API wrapper
├── event_processor.py          # Event → Constraints converter
├── notification_service.py     # Email/Calendar notifications
├── scheduler.py                # Scheduling logic
├── calendar_agent.py          # Main entry point
├── ARCHITECTURE.md            # Architecture documentation
├── CALENDAR_SETUP.md          # This file
├── credentials.json           # OAuth credentials (gitignored)
└── token.json                 # OAuth tokens (gitignored)
```

## Troubleshooting

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Rename to `credentials.json`
- Place in project root

### "Permission denied" errors
- Check that Calendar API and Gmail API are enabled
- Re-authenticate by deleting `token.json` and running again

### No events found
- Check that events are in your primary calendar
- Ensure events have "lunch" keywords or are between 11 AM - 2 PM
- Verify OAuth scopes include calendar.readonly

### Email not sending
- Check `NOTIFICATION_EMAIL` in `.env`
- Ensure Gmail API is enabled
- Verify OAuth scopes include gmail.send

## Notes

- Events are marked as "processed" to avoid duplicates
- Processed events stored in `processed_events.json`
- Calendar events updated with recommendations in description
- All sensitive files (`token.json`, `credentials.json`) are gitignored

