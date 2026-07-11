import requests

def get_weather():

    url = "https://api.open-meteo.com/v1/forecast?latitude=17.385&longitude=78.4867&current_weather=true"

    data = requests.get(url).json()

    return data["current_weather"]["temperature"]