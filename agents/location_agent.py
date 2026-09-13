from typing import List

def extract_location(user_input: str) -> str:
    """
    Extract location/city from user input.
    
    Args:
        user_input: Text input to search for location
        
    Returns:
        Detected city name or "Unknown location"
    """
    cities: List[str] = [
        "Hyderabad",
        "Vijayawada",
        "Bangalore",
        "Chennai",
        "Delhi",
        "Mumbai"
    ]

    try:
        for city in cities:
            if city.lower() in user_input.lower():
                return city
    except Exception as e:
        print(f"Error in location extraction: {str(e)}")

    return "Unknown location"