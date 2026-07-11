from agents.location_agent import extract_location
from agents.hospital_agent import find_hospitals
from agents.weather_agent import get_weather

def coordinate_agents(user_input):

    result = {}

    # Agent 1: Location
    location = extract_location(user_input)
    result["location"] = location

    # Agent 2: Hospitals
    hospitals = find_hospitals(location)
    result["hospitals"] = hospitals

    # Agent 3: Weather
    temperature = get_weather()
    result["temperature"] = temperature

    return result