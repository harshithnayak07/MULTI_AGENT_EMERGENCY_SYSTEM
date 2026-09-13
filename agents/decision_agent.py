from typing import List

def analyze_emergency(location: str, hospitals: List[str], temperature: float) -> None:
    """
    Analyze and display emergency information (for CLI use).
    
    Args:
        location: Detected location
        hospitals: List of nearby hospitals
        temperature: Current temperature
    """
    print("\nEmergency Analysis")
    print("---------------------------")

    print("Location:", location)

    print("Temperature:", temperature, "°C")

    print("\nNearby Hospitals:")

    for h in hospitals[:3]:
        print("-", h)

    print("\nSuggested Action:")

    print("Call ambulance: 108")

    print("Visit nearest hospital immediately")