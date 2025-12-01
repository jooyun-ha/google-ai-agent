"""
Lunza - A hyper-efficient, location-aware menu reasoning agent
"""
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. SETUP: API Key and Client Initialization ---
# The Client will automatically pick up the GEMINI_API_KEY from your environment variables.
# We'll also check for GOOGLE_API_KEY for backward compatibility
api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("🚨 ERROR: Could not find API key.")
    print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

# Set the API key for the client
os.environ['GEMINI_API_KEY'] = api_key

try:
    client = genai.Client(api_key=api_key)
    # Using Pro for complex reasoning, or Flash for faster demos
    MODEL_NAME = "gemini-2.5-pro" 
except Exception as e:
    print("🚨 ERROR: Could not initialize Gemini Client.")
    print(f"Error: {str(e)}")
    print("Please ensure your API key is set correctly as an environment variable.")
    exit()

# --- 2. THE TOOL: Mock Calendar Function ---
def get_next_meeting(user_id: str) -> str:
    """
    Retrieves the next scheduled event from the user's Google Calendar.
    This mock function returns fixed data for demonstration purposes.
    Args:
        user_id: The ID of the user whose calendar to check.
    Returns:
        A JSON string containing the event details.
    """
    print(f"\n⚙️ TOOL EXECUTED: Fetching calendar for User {user_id}...")
    
    # --- MOCK DATA FOR MVP ---
    if user_id == "lunza_user":
        event_data = {
            "title": "Q3 Strategy Planning",
            "location": "The Office HQ - 20th Floor Conference Room",
            "time": "12:30 PM",
            "attendees": ["Alice", "Bob", "User"],
            "notes": "Need high-energy, brain-fueling food. No heavy carbs."
        }
        return json.dumps(event_data)
    else:
        return json.dumps({"error": "User not found"})

# --- 3. AGENT LOGIC: The System Prompt ---
# This is the "brain" of Lunza. The model must follow these instructions rigorously.
SYSTEM_PROMPT = """
You are Lunza, a hyper-efficient, location-aware menu reasoning agent.
Your primary goal is to detect a 'lunch meeting' from the calendar and recommend a
suitable menu item based on the location and the meeting notes/attendees.

Always follow these steps:
1. If the user asks for a lunch recommendation, immediately call the `get_next_meeting` tool with the user_id 'lunza_user'.
2. Use the returned meeting location and notes to formulate a hyper-relevant recommendation.
3. The final answer must be structured, clear, and actionable.
"""

# --- 4. THE EXECUTION LOOP ---
def run_lunza_agent(prompt: str):
    """Manages the conversation and function calling loop."""
    print(f"👤 USER: {prompt}")
    
    # 1. Start the Chat Session with the System Prompt and Tools
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[get_next_meeting] # Pass the Python function itself
    )
    chat = client.chats.create(
        model=MODEL_NAME,
        config=config
    )

    # 2. Send the Initial Prompt
    response = chat.send_message(prompt)

    # 3. The Function Calling Loop
    while response.function_calls:
        print("🤖 AGENT: Function call requested...")
        
        # We assume one call for this demo, but the loop supports multiple calls!
        for function_call in response.function_calls:
            function_name = function_call.name
            args = dict(function_call.args)
            
            # --- Map the function name to the actual Python function ---
            if function_name == "get_next_meeting":
                # Execute the function with the arguments provided by Gemini
                tool_output = get_next_meeting(**args)
                
                # 4. Send the Function's RESULT back to Gemini
                print(f"⬆️ Sending result back to Agent: {tool_output[:50]}...")
                response = chat.send_message(
                    contents=[types.Part.from_function_response(
                        name=function_name,
                        response={"result": tool_output}
                    )]
                )
            else:
                raise ValueError(f"Unknown function: {function_name}")
                
    # 5. Output the Final Recommendation
    print("\n✅ LUNZA FINAL RECOMMENDATION:")
    print("------------------------------")
    print(response.text)
    print("------------------------------")

def main():
    """Main interaction loop"""
    print("🤖 Lunza - Location-Aware Menu Reasoning Agent")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        try:
            run_lunza_agent(user_input)
            print()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

if __name__ == "__main__":
    main()

