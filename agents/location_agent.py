def extract_location(user_input):

    cities = [
        "Hyderabad",
        "Vijayawada",
        "Bangalore",
        "Chennai",
        "Delhi",
        "Mumbai"
    ]

    for city in cities:
        if city.lower() in user_input.lower():
            return city

    return "Unknown location"