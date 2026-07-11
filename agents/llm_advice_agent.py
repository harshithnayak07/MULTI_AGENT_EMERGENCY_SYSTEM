import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_llm_advice(emergency_text, location, temperature):

    prompt = f"""
You are an emergency medical assistant.

Emergency description: {emergency_text}
Location: {location}
Temperature: {temperature}°C

Provide short first-aid advice and safety steps.
"""

    try:

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        result = response.json()

        if response.status_code == 200 and "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Groq API Error: {response.status_code} - {json.dumps(result, indent=2)}")
            return "AI advice unavailable right now. Please call ambulance 108 immediately."

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return "AI advice service temporarily unavailable. Call emergency services immediately."
