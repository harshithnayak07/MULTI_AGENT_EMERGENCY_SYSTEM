from agents.location_agent import extract_location
from agents.hospital_agent import find_hospitals
from agents.weather_agent import get_weather
from agents.decision_agent import analyze_emergency

user_input = input("Describe the emergency: ")

location = extract_location(user_input)

hospitals = find_hospitals(location)

temperature = get_weather()

analyze_emergency(location, hospitals, temperature)