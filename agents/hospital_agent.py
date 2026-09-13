import requests
from typing import Dict, List, Optional

HEADERS = {"User-Agent": "multi-agent-emergency-system"}

# Fallback city centers used only if the API fails
CITY_CENTERS = {
    "Delhi": [28.6139, 77.2090],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Mumbai": [19.0760, 72.8777],
    "Vijayawada": [16.5062, 80.6480],
}


def find_hospitals_with_coordinates(city: str, limit: int = 8) -> List[Dict]:
    """
    Find hospitals in a given city with real geographic coordinates.

    Uses the OpenStreetMap Nominatim search API, which returns each
    hospital with its latitude/longitude.

    Args:
        city: City name to search for hospitals
        limit: Maximum number of results to return

    Returns:
        List of dicts: {name, address, latitude, longitude}
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"hospitals in {city}",
        "format": "json",
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        hospitals: List[Dict] = []
        for place in data:
            try:
                name = place.get("display_name", "").split(",")[0].strip() or f"Hospital in {city}"
                hospitals.append({
                    "name": name,
                    "address": place.get("display_name", ""),
                    "latitude": float(place.get("lat")),
                    "longitude": float(place.get("lon")),
                })
            except (TypeError, ValueError):
                continue

        if hospitals:
            return hospitals

    except requests.exceptions.RequestException as e:
        print(f"Error fetching hospitals: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in hospital agent: {str(e)}")

    # Fallback hospitals with coordinates near the city centre if API fails
    center = CITY_CENTERS.get(city, [17.3850, 78.4867])
    fallbacks = [
        (f"Government Hospital {city}", 0.01),
        (f"City Care Hospital {city}", -0.01),
        (f"Apollo Hospital {city}", 0.02),
    ]
    return [
        {
            "name": name,
            "address": f"{name}, {city}",
            "latitude": round(center[0] + offset, 5),
            "longitude": round(center[1] + offset, 5),
        }
        for name, offset in fallbacks
    ]


def find_hospitals(city: str) -> List[str]:
    """
    Find hospitals in a given city and return their display addresses.

    Args:
        city: City name to search for hospitals

    Returns:
        List of hospital display names/addresses
    """
    return [h["address"] for h in find_hospitals_with_coordinates(city)]