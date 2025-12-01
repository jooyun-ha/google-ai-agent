"""
Lunza - Enhanced Location-Aware Menu Reasoning Agent
Architecture: Planner Agent → Maps Tool → Health Scoring → Session Memory → Final Agent
"""
import os
import json
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. SETUP: API Key and Client Initialization ---
api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
google_places_api_key = os.getenv('GOOGLE_PLACES_API_KEY')  # Optional for now

if not api_key:
    print("🚨 ERROR: Could not find API key.")
    print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

os.environ['GEMINI_API_KEY'] = api_key

try:
    client = genai.Client(api_key=api_key)
    MODEL_NAME = "gemini-2.5-pro" 
except Exception as e:
    print("🚨 ERROR: Could not initialize Gemini Client.")
    print(f"Error: {str(e)}")
    exit()

# --- 2. SESSION MEMORY MODULE ---
class SessionMemory:
    """Stores last 3 selections to avoid repeating recent cuisines"""
    def __init__(self):
        self.recent_selections = []
        self.max_history = 3
    
    def add_selection(self, restaurant_name: str, cuisine_type: str):
        """Add a selection to memory"""
        self.recent_selections.append({
            "name": restaurant_name,
            "cuisine": cuisine_type
        })
        if len(self.recent_selections) > self.max_history:
            self.recent_selections.pop(0)
    
    def get_recent_cuisines(self) -> List[str]:
        """Get list of recently selected cuisines"""
        return [item["cuisine"] for item in self.recent_selections]
    
    def should_avoid(self, cuisine_type: str) -> bool:
        """Check if a cuisine should be avoided (recently selected)"""
        return cuisine_type.lower() in [c.lower() for c in self.get_recent_cuisines()]

session_memory = SessionMemory()

# --- 3. PLANNER AGENT (Gemini API) ---
PLANNER_PROMPT = """
You are a meeting details extraction agent. Extract key information from user queries about lunch meetings.

Extract and return a JSON object with these fields:
- area: location/area (e.g., "San Francisco", "near GitHub HQ")
- venue: specific venue if mentioned
- time: meeting time if mentioned
- diet: dietary restrictions (e.g., "diabetes", "vegetarian", "keto")
- health: health considerations (e.g., "low carb", "high protein", "brain fuel")

Return ONLY valid JSON, no additional text.
"""

def planner_agent_extract(user_query: str) -> Dict:
    """Extract meeting details and constraints using Gemini"""
    try:
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=PLANNER_PROMPT
            )
        )
        response = chat.send_message(f"Extract details from: {user_query}")
        
        # Parse JSON response
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"⚠️ Planner error: {e}")
        # Return default structure
        return {
            "area": "San Francisco",
            "venue": None,
            "time": None,
            "diet": None,
            "health": None
        }

# --- 4. MAPS TOOL (Google Places/Maps API Wrapper) ---
def search_nearby_restaurants(area: str, venue: Optional[str] = None) -> List[Dict]:
    """
    Search nearby restaurants using Google Places API.
    For MVP, returns mock data. Replace with actual API calls when ready.
    """
    print(f"\n⚙️ MAPS TOOL: Searching restaurants near {area}...")
    
    # MOCK DATA - Replace with actual Google Places API call
    mock_restaurants = [
        {
            "name": "Sweetgreen",
            "address": "88 2nd St, San Francisco, CA 94105",
            "rating": 4.5,
            "price": "$$",
            "distance": "0.3 miles",
            "tags": ["healthy", "salads", "diabetes-friendly", "low-carb"],
            "cuisine": "Healthy American"
        },
        {
            "name": "Chipotle",
            "address": "88 4th St, San Francisco, CA 94103",
            "rating": 4.2,
            "price": "$",
            "distance": "0.5 miles",
            "tags": ["mexican", "bowls", "customizable", "protein"],
            "cuisine": "Mexican"
        },
        {
            "name": "Souvla",
            "address": "517 Hayes St, San Francisco, CA 94102",
            "rating": 4.7,
            "price": "$$",
            "distance": "0.8 miles",
            "tags": ["greek", "mediterranean", "healthy", "fresh"],
            "cuisine": "Greek"
        },
        {
            "name": "The Plant Cafe Organic",
            "address": "301 Mission St, San Francisco, CA 94105 (located in the lobby of the building)",
            "rating": 4.4,
            "price": "$$",
            "distance": "0.6 miles",
            "tags": ["vegetarian", "organic", "healthy", "sustainable"],
            "cuisine": "Vegetarian"
        },
        {
            "name": "Blue Bottle Coffee + Kitchen",
            "address": "66 Mint St, San Francisco, CA 94103",
            "rating": 4.3,
            "price": "$$",
            "distance": "0.4 miles",
            "tags": ["cafe", "light meals", "coffee", "quick"],
            "cuisine": "Cafe"
        }
    ]
    
    # Filter by venue proximity if specified
    if venue:
        # In real implementation, would filter by actual distance from venue
        pass
    
    return mock_restaurants

# --- 5. HEALTH SCORING FUNCTION ---
def calculate_health_score(restaurant: Dict, diet: Optional[str], health: Optional[str]) -> int:
    """
    Rank restaurant based on diet & metabolic risks.
    Returns score from 0-100.
    """
    score = 50  # Base score
    
    tags = [tag.lower() for tag in restaurant.get("tags", [])]
    
    # Diabetes-friendly scoring
    if diet and "diabetes" in diet.lower():
        if "diabetes-friendly" in tags or "low-carb" in tags:
            score += 30
        if "healthy" in tags:
            score += 15
        if "high protein" in tags or "protein" in tags:
            score += 10
        if "sugar" in tags or "dessert" in tags:
            score -= 20
    
    # Health considerations
    if health:
        health_lower = health.lower()
        if "low carb" in health_lower and "low-carb" in tags:
            score += 25
        if "high protein" in health_lower and "protein" in tags:
            score += 20
        if "brain fuel" in health_lower and ("protein" in tags or "healthy" in tags):
            score += 15
    
    # General health indicators
    if "healthy" in tags:
        score += 10
    if "organic" in tags:
        score += 5
    
    # Rating boost
    rating = restaurant.get("rating", 0)
    score += (rating - 4.0) * 10  # Boost for ratings above 4.0
    
    # Avoid recently selected cuisines
    cuisine = restaurant.get("cuisine", "")
    if session_memory.should_avoid(cuisine):
        score -= 15
    
    return max(0, min(100, score))  # Clamp between 0-100

# --- 6. FINAL AGENT ANSWER (Gemini) ---
FINAL_AGENT_PROMPT = """
You are Lunza, a hyper-efficient, location-aware menu reasoning agent.
Your goal is to provide clear, actionable lunch recommendations with justifications.

Given restaurant options with health scores, provide:
1. Top 3 recommendations ranked by suitability
2. For each restaurant, ALWAYS include:
   - Restaurant name
   - Full address (as provided in the restaurant data)
3. Specific menu items to order at each place
4. Clear justification for each recommendation based on:
   - Health/dietary requirements
   - Location convenience
   - Meeting context

Format each recommendation like this:
**Restaurant:** [Name]
**Address:** [Full address]

Be concise, practical, and helpful.
"""

def final_agent_recommend(restaurants: List[Dict], constraints: Dict, user_query: str) -> str:
    """Generate final recommendation using Gemini"""
    try:
        # Prepare context
        scored_restaurants = []
        for restaurant in restaurants:
            score = calculate_health_score(
                restaurant,
                constraints.get("diet"),
                constraints.get("health")
            )
            restaurant_copy = restaurant.copy()
            restaurant_copy["health_score"] = score
            scored_restaurants.append(restaurant_copy)
        
        # Sort by health score (descending)
        scored_restaurants.sort(key=lambda x: x["health_score"], reverse=True)
        top_3 = scored_restaurants[:3]
        
        # Build context for final agent
        context = f"""
User Query: {user_query}

Constraints:
- Area: {constraints.get('area', 'N/A')}
- Venue: {constraints.get('venue', 'N/A')}
- Diet: {constraints.get('diet', 'N/A')}
- Health: {constraints.get('health', 'N/A')}

Top Restaurant Options (ranked by health score):
{json.dumps(top_3, indent=2)}

Recent selections to avoid: {session_memory.get_recent_cuisines()}
"""
        
        chat = client.chats.create(
            model=MODEL_NAME,
            config=types.GenerateContentConfig(
                system_instruction=FINAL_AGENT_PROMPT
            )
        )
        response = chat.send_message(context)
        
        # Update session memory with top choice
        if top_3:
            top_choice = top_3[0]
            session_memory.add_selection(
                top_choice["name"],
                top_choice.get("cuisine", "Unknown")
            )
        
        return response.text
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"

# --- 7. INTERACTIVE PROMPT FOR MISSING INFO ---
def prompt_for_missing_info(constraints: Dict) -> Dict:
    """Prompt user for missing information to avoid null values"""
    updated_constraints = constraints.copy()
    
    questions = []
    
    if not updated_constraints.get("venue"):
        questions.append(("venue", "What's the specific venue or location for your meeting? (e.g., 'GitHub HQ', 'downtown office', or 'skip' if not applicable)"))
    
    if not updated_constraints.get("time"):
        questions.append(("time", "What time is your meeting? (e.g., '12:30 PM', '1:00 PM', or 'skip' if not specified)"))
    
    if not updated_constraints.get("health"):
        questions.append(("health", "Any specific health considerations? (e.g., 'low carb', 'high protein', 'brain fuel', or 'skip' if none)"))
    
    if questions:
        print("\n💬 I need a bit more information to give you the best recommendation:")
        print("-" * 60)
        
        for field, question in questions:
            answer = input(f"{question}\n   Your answer: ").strip()
            if answer.lower() not in ['skip', 'none', 'n/a', '']:
                updated_constraints[field] = answer
            print()
    
    return updated_constraints

# --- 8. MAIN EXECUTION FLOW ---
def run_enhanced_lunza(user_query: str, skip_prompts: bool = False, pre_extracted_constraints: Optional[Dict] = None):
    """
    Main execution flow: Planner → Maps → Health Scoring → Memory → Final Agent
    
    Args:
        user_query: User's query string
        skip_prompts: If True, skip interactive prompts (for calendar mode)
        pre_extracted_constraints: Pre-extracted constraints dict (for calendar mode)
    """
    print(f"\n👤 USER: {user_query}")
    print("\n" + "="*60)
    
    # Step 1: Planner Agent - Extract constraints
    print("📋 STEP 1: Planner Agent extracting meeting details...")
    if pre_extracted_constraints:
        # Use pre-extracted constraints (from calendar)
        constraints = pre_extracted_constraints
        print(f"   Using pre-extracted constraints: {json.dumps(constraints, indent=2)}")
    else:
        constraints = planner_agent_extract(user_query)
        print(f"   Extracted: {json.dumps(constraints, indent=2)}")
    
    # Step 1.5: Prompt for missing information (skip if in calendar mode)
    if not skip_prompts:
        original_constraints = constraints.copy()
        constraints = prompt_for_missing_info(constraints)
        if constraints != original_constraints:
            print(f"   Updated constraints: {json.dumps(constraints, indent=2)}")
    
    # Step 2: Maps Tool - Search restaurants
    print(f"\n🗺️  STEP 2: Maps Tool searching restaurants...")
    restaurants = search_nearby_restaurants(
        constraints.get("area", "San Francisco"),
        constraints.get("venue")
    )
    print(f"   Found {len(restaurants)} restaurants")
    
    # Step 3: Health Scoring (done in final_agent_recommend)
    print(f"\n💊 STEP 3: Calculating health scores...")
    
    # Step 4: Final Agent - Generate recommendation
    print(f"\n🤖 STEP 4: Final Agent generating recommendation...")
    recommendation = final_agent_recommend(restaurants, constraints, user_query)
    
    # Output
    print("\n" + "="*60)
    print("✅ LUNZA FINAL RECOMMENDATION:")
    print("="*60)
    print(recommendation)
    print("="*60)

def main():
    """Main interaction loop"""
    print("🤖 Lunza Enhanced - Multi-Agent Menu Reasoning System")
    print("Architecture: Planner → Maps → Health Scoring → Memory → Final Agent")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            run_enhanced_lunza(user_input)
            print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            print()

if __name__ == "__main__":
    main()
