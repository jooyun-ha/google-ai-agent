"""
Simple Google AI Agent using Gemini API
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("⚠️  Please set GOOGLE_API_KEY in your .env file")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

def chat_with_agent(user_input):
    """Send a message to the AI agent and get a response"""
    try:
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    """Main interaction loop"""
    print("🤖 Google AI Agent - Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        print("Agent: ", end="")
        response = chat_with_agent(user_input)
        print(response)
        print()

if __name__ == "__main__":
    main()

