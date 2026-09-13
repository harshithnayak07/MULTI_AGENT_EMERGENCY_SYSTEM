import requests
import os
import json
from typing import Optional, Callable
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_llm_advice(emergency_text: str, location: str, temperature: float, 
                       stream_callback: Optional[Callable[[str], None]] = None) -> str:
    """
    Generate AI-powered emergency medical advice using Groq API.
    
    Args:
        emergency_text: Description of the emergency
        location: Location of the emergency
        temperature: Current temperature
        stream_callback: Optional callback function for streaming responses
        
    Returns:
        Generated medical advice or fallback message
    """
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
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": stream_callback is not None
            },
            timeout=30
        )

        if response.status_code != 200:
            print(f"Groq API Error: {response.status_code}")
            return "AI advice unavailable right now. Please call ambulance 108 immediately."

        if stream_callback:
            # Handle streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    stream_callback(content)
                        except json.JSONDecodeError:
                            continue
            return full_response
        else:
            # Handle non-streaming response
            result = response.json()

            if response.status_code == 200 and "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                print(f"Groq API Error: {response.status_code} - {json.dumps(result, indent=2)}")
                return "AI advice unavailable right now. Please call ambulance 108 immediately."

    except requests.exceptions.Timeout:
        print("Groq API timeout")
        return "AI advice service timed out. Call emergency services immediately."
    except requests.exceptions.RequestException as e:
        print(f"Groq API request error: {str(e)}")
        return "AI advice unavailable right now. Please call ambulance 108 immediately."
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return "AI advice service temporarily unavailable. Call emergency services immediately."
