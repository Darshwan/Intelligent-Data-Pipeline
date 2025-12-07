import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import os
from datetime import datetime

# Config
st.set_page_config(
    page_title="Nepal Data Hub - Earthquakes",
    layout="wide",
    page_icon="🇳🇵"
)

# API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Title
st.title("🇳🇵 Nepal Data Hub: Real-Time Earthquake Monitor")
st.markdown("Monitor real-time earthquake activities in Nepal and surrounding regions.")

# Sidebar Filters
st.sidebar.header("Filters")
min_mag = st.sidebar.slider("Minimum Magnitude", 0.0, 9.0, 2.0, 0.1)
limit = st.sidebar.slider("Number of Events", 10, 500, 100)

# Fetch Data
@st.cache_data(ttl=60)
def fetch_data(min_mag, limit):
    try:
        params = {"min_mag": min_mag, "limit": limit}
        response = requests.get(f"{API_URL}/earthquakes", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []

data = fetch_data(min_mag, limit)

if data:
    df = pd.DataFrame(data)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Events", len(df))
    col2.metric("Max Magnitude", df['magnitude'].max() if not df.empty else 0)
    col3.metric("Latest Event", df['time'].max().split('T')[0] if not df.empty else "-")

    # Map
    st.subheader("Earthquake Map")
    if not df.empty:
        # Define a layer to display on a map
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            pickable=True,
            opacity=0.8,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=5,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position="[longitude, latitude]",
            get_radius="magnitude * 5000",
            get_fill_color=[255, 140, 0],
            get_line_color=[0, 0, 0],
        )

        # Set the viewport location
        view_state = pdk.ViewState(
            latitude=28.3949,
            longitude=84.1240,
            zoom=6,
            pitch=0,
        )

        # Render
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "{place}\nMagnitude: {magnitude}\nTime: {time}"}
        )
        st.pydeck_chart(r)

    # Data Table
    st.subheader("Recent Events")
    st.dataframe(df[['time', 'magnitude', 'place', 'depth', 'latitude', 'longitude']])

else:
    st.info("No earthquake data found matching criteria.")

# Weather Section
st.markdown("---")
st.title("Weather Conditions")

@st.cache_data(ttl=60)
def fetch_weather():
    try:
        response = requests.get(f"{API_URL}/weather")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

weather_data = fetch_weather()
if weather_data:
    wdf = pd.DataFrame(weather_data)
    
    # Display latest weather for each city
    latest_weather = wdf.sort_values('time', ascending=False).drop_duplicates('city')
    
    cols = st.columns(len(latest_weather))
    for idx, (_, row) in enumerate(latest_weather.iterrows()):
        with cols[idx % 3]: # Wrap around if many cities
            st.metric(
                label=row['city'],
                value=f"{row['temperature']}°C",
                delta=row['condition']
            )
    
    st.subheader("Recent measurements")
    st.dataframe(wdf)

# Flood Alerts Section
st.markdown("---")
st.title("🌊 River Watch (Flood Alerts)")

@st.cache_data(ttl=60)
def fetch_flood_alerts():
    try:
        response = requests.get(f"{API_URL}/flood")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []

flood_data = fetch_flood_alerts()
if flood_data:
    fdf = pd.DataFrame(flood_data)
    
    # Latest status per station
    latest_flood = fdf.sort_values('time', ascending=False).drop_duplicates('station')
    
    for _, row in latest_flood.iterrows():
        status_color = "red" if row['status'] == "Danger" else "orange" if row['status'] == "Warning" else "green"
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"**{row['station']}**")
            col2.metric("Water Level", f"{row['water_level']}m")
            col3.metric("Danger Level", f"{row['danger_level']}m")
            col4.markdown(f":{status_color}[**{row['status']}**]")

    st.subheader("Recent River Levels")
    st.dataframe(fdf)

# Footer
st.markdown("---")
st.markdown("Built with **FastAPI**, **TimescaleDB**, **Apache Kafka** & **Streamlit**")
