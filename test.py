from google import genai
import os

# 1. HARDCODE for one final test to rule out .env issues
# Copy EXACTLY from AI Studio: https://aistudio.google.com/app/apikey
MY_KEY = "***************************************" 

# 2. Initialize the MODERN client
# We specify the api_key here. Do NOT rely on os.getenv for this specific test.
client = genai.Client(api_key=MY_KEY)

print("--- Starting Connection Test ---")

try:
    # Use the 2.0 Flash model (latest)
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents="Say 'Backend Verified'"
    )
    print(f"✅ SUCCESS: {response.text}")
except Exception as e:
    print(f"❌ FAILED AGAIN: {e}")
    print("\nIf you see 'API_KEY_INVALID' here, the key you copied is objectively wrong.")
    print("Check if you accidentally copied a space or if the key was truncated.")