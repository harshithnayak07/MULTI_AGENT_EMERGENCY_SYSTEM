import requests

def find_hospitals(city):

    url = f"https://nominatim.openstreetmap.org/search?q=hospitals+in+{city}&format=json&limit=5"

    headers = {
        "User-Agent": "multi-agent-emergency-system"
    }

    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()

        hospitals = []

        for place in data:
            hospitals.append(place["display_name"])

        if hospitals:
            return hospitals

    except:
        pass

    # fallback hospitals if API fails
    return [
        f"Government Hospital {city}",
        f"City Care Hospital {city}",
        f"Apollo Hospital {city}"
    ]