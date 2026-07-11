import streamlit as st
from agents.location_agent import extract_location
from agents.hospital_agent import find_hospitals
from agents.weather_agent import get_weather
from agents.coordinator_agent import coordinate_agents
from agents.voice_agent import listen_emergency
from agents.llm_advice_agent import generate_llm_advice
import pydeck as pdk
import pandas as pd


city_coordinates = {
    "Delhi": [28.6139, 77.2090],
    "Bangalore": [12.9716, 77.5946],
    "Hyderabad": [17.3850, 78.4867],
    "Chennai": [13.0827, 80.2707],
    "Mumbai": [19.0760, 72.8777]
}


def show_results(result, emergency_text):

    location = result["location"]

    st.subheader("Emergency Analysis")

    st.write("Location:", location)
    st.write("Temperature:", result["temperature"], "°C")

    st.subheader("Nearby Hospitals")

    for h in result["hospitals"][:3]:
        st.write("-", h)

    # MAP SECTION
    if location in city_coordinates:

        coords = city_coordinates[location]
        lat = coords[0]
        lon = coords[1]

        map_data = pd.DataFrame({
            "lat": [lat],
            "lon": [lon]
        })

        st.subheader("Emergency Location Map")
        map_url = f"https://www.openstreetmap.org/export/embed.html?bbox={lon-0.05}%2C{lat-0.05}%2C{lon+0.05}%2C{lat+0.05}&layer=mapnik&marker={lat}%2C{lon}"

        st.markdown(f'<iframe src="{map_url}" width="100%" height="400"></iframe>', unsafe_allow_html=True)

    # LLM ADVICE SECTION
    advice = generate_llm_advice(emergency_text, location, result["temperature"])

    st.subheader("AI Emergency Advice")

    st.write(advice)

    st.subheader("Recommended Action")

    st.write("Call ambulance: 108")
    st.write("Go to nearest hospital immediately")


st.title("AI Emergency Response Multi-Agent System")

st.write("Describe the emergency situation")

user_input = st.text_input("Emergency Description")


# TEXT INPUT
if st.button("Analyze Emergency"):

    result = coordinate_agents(user_input)

    show_results(result, user_input)


# VOICE INPUT
if st.button("Use Voice Input"):

    emergency_text = listen_emergency()

    st.write("Detected Speech:", emergency_text)

    result = coordinate_agents(emergency_text)

    show_results(result, emergency_text)