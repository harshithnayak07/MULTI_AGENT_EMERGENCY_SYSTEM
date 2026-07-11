import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

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
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        result = response.json()

        if "choices" in result:
            return result["choices"][0]["message"]["content"]

        else:
            return "AI advice unavailable right now. Please call ambulance 108 immediately."

    except Exception as e:
        return "AI advice service temporarily unavailable. Call emergency services immediately."