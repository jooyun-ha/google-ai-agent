# Lunza - Location-Aware Menu Reasoning Agent

A multi-agent AI system that recommends lunch options based on meeting context, location, and health requirements.

## 🎯 Quick Start for Judges

**Want to test immediately?** Use the demo mode (no setup required):

```bash
python3 calendar_agent_demo.py
```

See [JUDGES_GUIDE.md](JUDGES_GUIDE.md) for detailed testing instructions.

## 📚 Project Versions

This project has **3 versions** across different branches:

### 1. `main` Branch - Simple Agent
**Location:** `main` branch  
**Features:**
- Basic Gemini API integration
- Simple chat interface
- Manual query input

**Run:**
```bash
git checkout main
python3 agent.py
```

### 2. `alternative-version` Branch - Enhanced Multi-Agent System
**Location:** `alternative-version` branch  
**Features:**
- Multi-agent architecture (Planner → Maps → Health Scoring → Final Agent)
- Health scoring algorithm
- Session memory (avoids repeating cuisines)
- Interactive prompts for missing information

**Run:**
```bash
git checkout alternative-version
python3 agent.py
```

### 3. `calendar-integration` Branch - Calendar Integration (Current)
**Location:** `calendar-integration` branch (you are here)  
**Features:**
- ✅ All features from `alternative-version`
- ✅ Google Calendar API integration
- ✅ Automatic event processing
- ✅ Email notifications
- ✅ Demo mode for testing (no credentials needed)

**Run Demo Mode (Recommended for Judges):**
```bash
python3 calendar_agent_demo.py
```

**Run Real Calendar Mode:**
```bash
python3 calendar_agent.py --once
```

## 🏗️ Architecture

The system uses a pipeline of specialized components:

| Component                                      | Role                                         | Output                                    |
| ---------------------------------------------- | -------------------------------------------- | ----------------------------------------- |
| **Planner Agent (Gemini API)**                 | Extract meeting details & constraints        | `{area, venue, time, diet, health}`       |
| **Maps Tool (Google Places/Maps API Wrapper)** | Search nearby restaurants                    | `[{name, rating, price, distance, tags}]` |
| **Health Scoring Function**                    | Rank based on diet & metabolic risks         | `0–100 scores`                            |
| **Session Memory Module**                      | Avoid repeating recent cuisines              | Stores last 3 selections                  |
| **Final Agent Answer (Gemini)**                | Deliver clear lunch recommendation + reasons | Top 3 + menus + justification             |

## 🚀 Setup

### For Demo Mode (No Setup Required)
```bash
# Just run it!
python3 calendar_agent_demo.py
```

### For Real Calendar Integration

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up your API keys:**
   - Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - (Optional) Get Google Places API key from [Google Cloud Console](https://console.cloud.google.com/)
   - Create a `.env` file and add:
     ```
     GOOGLE_API_KEY=your_gemini_api_key_here
     GOOGLE_PLACES_API_KEY=your_places_api_key_here  # Optional
     ```

3. **For Calendar Integration:**
   - See [CALENDAR_SETUP.md](CALENDAR_SETUP.md) for detailed instructions
   - Requires Google Cloud project and OAuth credentials

## 📖 Documentation

- **[JUDGES_GUIDE.md](JUDGES_GUIDE.md)** - Testing guide for judges
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed architecture documentation
- **[CALENDAR_SETUP.md](CALENDAR_SETUP.md)** - Calendar integration setup guide

## 🧪 Testing

### For Judges
```bash
# Demo mode (recommended - no setup needed)
python3 calendar_agent_demo.py
```

### For Developers
```bash
# Manual mode
python3 agent.py

# Calendar mode (one-time check)
python3 calendar_agent.py --once

# Calendar mode (continuous)
python3 calendar_agent.py
```

## 📁 Project Structure

```
google-ai-agent/
├── agent.py                    # Core Lunza agent
├── calendar_agent.py           # Real calendar mode
├── calendar_agent_demo.py      # Demo mode (for judges)
├── calendar_integration.py     # Calendar API wrapper
├── event_processor.py          # Event → Constraints converter
├── notification_service.py     # Email/Calendar notifications
├── scheduler.py                # Scheduling logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── JUDGES_GUIDE.md            # Testing guide
├── ARCHITECTURE.md            # Architecture docs
└── CALENDAR_SETUP.md          # Setup guide
```

## 🔄 Switching Between Versions

```bash
# View all branches
git branch

# Switch to main (simple version)
git checkout main

# Switch to alternative-version (enhanced)
git checkout alternative-version

# Switch to calendar-integration (current)
git checkout calendar-integration
```

## 💡 Features by Version

| Feature | main | alternative-version | calendar-integration |
|---------|------|---------------------|---------------------|
| Basic chat | ✅ | ✅ | ✅ |
| Multi-agent system | ❌ | ✅ | ✅ |
| Health scoring | ❌ | ✅ | ✅ |
| Session memory | ❌ | ✅ | ✅ |
| Calendar integration | ❌ | ❌ | ✅ |
| Demo mode | ❌ | ❌ | ✅ |
| Email notifications | ❌ | ❌ | ✅ |

## 🤝 For Judges

**Recommended Testing Flow:**
1. Start with `calendar_agent_demo.py` (no setup needed)
2. Review `JUDGES_GUIDE.md` for testing checklist
3. Check `ARCHITECTURE.md` for technical details
4. Optionally test other branches for comparison

## 📝 License

This project is for demonstration purposes.
