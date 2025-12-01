# Judges Guide - Testing Lunza Calendar Agent

## 🎯 Quick Start

### Option 1: Demo Mode (Recommended - No Setup Required)

**Perfect for judges!** Uses mock calendar data - no credentials or calendar access needed.

```bash
python3 calendar_agent_demo.py
```

**What it does:**
- ✅ Shows full calendar integration flow
- ✅ Uses mock calendar events (no privacy concerns)
- ✅ Demonstrates constraint extraction
- ✅ Generates real recommendations
- ✅ No Google Cloud setup required

### Option 2: Real Calendar Mode (Optional)

If judges want to test with their own calendar:

1. **Set up Google Cloud** (see `CALENDAR_SETUP.md`)
2. **Get credentials.json**
3. **Run**: `python3 calendar_agent.py --once`

## 📋 What the Demo Shows

The demo processes **2 mock calendar events**:

1. **Team Lunch Meeting**
   - Location: San Francisco, near GitHub HQ
   - Diet: Diabetes-friendly
   - Health: Low-carb options

2. **Client Lunch**
   - Location: Downtown San Francisco
   - Diet: Vegetarian

**Output includes:**
- Event extraction from calendar
- Constraint parsing (area, venue, diet, health)
- Restaurant search and health scoring
- Top 3 recommendations with addresses
- Menu suggestions and justifications

## 🏗️ Architecture Overview

```
Mock Calendar Events
    ↓
Event Processor (extracts constraints)
    ↓
Lunza Pipeline:
  - Planner Agent
  - Maps Tool
  - Health Scoring
  - Session Memory
  - Final Agent
    ↓
Recommendations Generated
```

## 📁 Key Files

- `calendar_agent_demo.py` - **Demo mode (use this!)**
- `calendar_agent.py` - Real calendar mode
- `agent.py` - Core Lunza agent
- `ARCHITECTURE.md` - Full architecture details
- `CALENDAR_SETUP.md` - Setup instructions

## ✅ Testing Checklist

- [ ] Run demo mode: `python3 calendar_agent_demo.py`
- [ ] Verify constraints are extracted correctly
- [ ] Check recommendations are generated
- [ ] Review restaurant addresses and menu suggestions
- [ ] (Optional) Test with real calendar

## 🔍 What to Look For

1. **Constraint Extraction**
   - Correctly identifies: area, venue, time, diet, health
   - Handles missing information gracefully

2. **Recommendation Quality**
   - Top 3 restaurants with addresses
   - Specific menu items suggested
   - Clear justifications
   - Health/dietary requirements met

3. **System Flow**
   - Events processed automatically
   - No duplicate processing
   - Clean output and error handling

## 💡 Features Demonstrated

- ✅ Multi-agent architecture
- ✅ Calendar integration
- ✅ Health scoring algorithm
- ✅ Session memory (avoids repeats)
- ✅ Location-aware recommendations
- ✅ Dietary constraint handling

## 🐛 Troubleshooting

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"API key error"**
- Check `.env` file has `GOOGLE_API_KEY` set
- Demo mode still needs Gemini API key for recommendations

**"No recommendations generated"**
- Check internet connection (needs Gemini API)
- Verify API key is valid

## 📞 Questions?

- Architecture: See `ARCHITECTURE.md`
- Setup: See `CALENDAR_SETUP.md`
- Code: Check individual `.py` files

---

**For judges:** The demo mode (`calendar_agent_demo.py`) is the best way to test without any setup. It demonstrates the full system capabilities using mock data.

