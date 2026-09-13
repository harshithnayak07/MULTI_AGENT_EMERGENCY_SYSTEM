import requests
from typing import Optional

def get_weather(latitude: float = 17.385, longitude: float = 78.4867) -> Optional[float]:
    """
    Get current weather temperature for given coordinates.
    
    Args:
        latitude: Latitude coordinate (default: Hyderabad)
        longitude: Longitude coordinate (default: Hyderabad)
        
    Returns:
        Current temperature in Celsius or None if failed
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if "current_weather" in data and "temperature" in data["current_weather"]:
            return data["current_weather"]["temperature"]
        else:
            print("Weather data format unexpected")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error in weather agent: {str(e)}")
        return None