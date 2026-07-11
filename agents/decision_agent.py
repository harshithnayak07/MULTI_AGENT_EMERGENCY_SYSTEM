def analyze_emergency(location, hospitals, temperature):

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