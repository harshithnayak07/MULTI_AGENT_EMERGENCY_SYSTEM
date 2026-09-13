from agents.location_agent import extract_location
from agents.hospital_agent import find_hospitals
from agents.weather_agent import get_weather
from typing import Dict, Any

def coordinate_agents(user_input: str) -> Dict[str, Any]:
    """
    Coordinate all agents to analyze emergency situation.
    
    Args:
        user_input: Emergency description from user
        
    Returns:
        Dictionary containing location, hospitals, and temperature data
    """
    result = {}

    try:
        # Agent 1: Location
        location = extract_location(user_input)
        result["location"] = location

        # Agent 2: Hospitals
        hospitals = find_hospitals(location)
        result["hospitals"] = hospitals

        # Agent 3: Weather
        temperature = get_weather()
        result["temperature"] = temperature

        result["success"] = True
    except Exception as e:
        print(f"Error in coordinator agent: {str(e)}")
        result["success"] = False
        result["error"] = str(e)

    return result