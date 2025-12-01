# Google AI Agent

A simple AI agent experiment built with Google's Gemini API.

## 🎯 For Judges - Start Here!

**👉 Switch to the `calendar-integration` branch for the full demo:**

```bash
git checkout calendar-integration
python3 calendar_agent_demo.py
```

See the [calendar-integration branch](https://github.com/jooyun-ha/google-ai-agent/tree/calendar-integration) for:
- ✅ Full multi-agent system
- ✅ Calendar integration
- ✅ Demo mode (no setup required)
- ✅ Complete documentation

## Project Versions

This project has **3 versions** across different branches:

1. **`main`** (this branch) - Simple agent with basic Gemini API
2. **`alternative-version`** - Enhanced multi-agent system
3. **`calendar-integration`** - Calendar integration + demo mode ⭐ **Recommended for judges**

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google API key:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file and add: `GOOGLE_API_KEY=your_api_key_here`

## Usage

Run the agent:
```bash
python agent.py
```

## Project Structure

- `agent.py` - Main agent code
- `requirements.txt` - Python dependencies
- `.env` - API keys (not committed to Git)

## Next Steps

- **For judges:** Check out `calendar-integration` branch for demo mode
- **For developers:** See other branches for enhanced features
