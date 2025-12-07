import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import numpy as np
import os
import time

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Nepal Data Hub",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
    }
    .district-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🇳🇵 Nepal Data Hub</h1>', unsafe_allow_html=True)
st.markdown("### Real-time Disaster & Civic Analytics Platform")

# Sidebar
with st.sidebar:
    st.header("Filters & Controls")
    
    data_sources = st.multiselect(
        "Data Sources",
        ["Earthquakes", "Weather", "Government Alerts", "Power Outages"],
        default=["Earthquakes", "Weather"]
    )
    
    time_range = st.select_slider(
        "Time Range",
        options=["1 hour", "6 hours", "24 hours", "7 days", "30 days"],
        value="24 hours"
    )
    
    districts = st.multiselect(
        "Districts",
        ["Kathmandu", "Lalitpur", "Bhaktapur", "Pokhara", "Biratnagar", "Butwal", "All"],
        default=["All"]
    )
    
    auto_refresh = st.checkbox("Auto-refresh", value=True)
    refresh_interval = st.slider("Refresh interval (seconds)", 10, 300, 60)

# Function to fetch data
@st.cache_data(ttl=60)
def fetch_dashboard_data():
    try:
        print(f"DEBUG: Connecting to {API_URL}/api/v1/dashboard")
        response = requests.get(f"{API_URL}/api/v1/dashboard", timeout=10)
        print(f"DEBUG: Status Code: {response.status_code}")
        if response.status_code != 200:
             print(f"DEBUG: Response Content: {response.text}")
        return response.json()
    except Exception as e:
        print(f"ERROR: Failed to fetch dashboard data: {e}")
        return {}

# Function to fetch correlations
@st.cache_data(ttl=300)
def fetch_correlations():
    try:
        response = requests.get(f"{API_URL}/api/v1/correlations", timeout=10)
        return response.json()
    except:
        return {}

# Main dashboard
data = fetch_dashboard_data()
correlations = fetch_correlations()

if not data:
    st.error("Could not fetch data. Make sure the API is running.")
    st.stop()

# Key metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    quake_count = len(data.get('earthquakes', []))
    st.markdown(f"""
    <div class="metric-card">
        <h3>Earthquakes (24h)</h3>
        <h1>{quake_count}</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if data.get('dashboard_stats'):
        weather_stats = data.get('dashboard_stats', {}).get('weather_updates', {})
        count = weather_stats.get('count', 0)
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <h3>Weather Stations</h3>
            <h1>{count}</h1>
        </div>
        """, unsafe_allow_html=True)

with col3:
    alert_count = len(data.get('alerts', []))
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
        <h3>Active Alerts</h3>
        <h1>{alert_count}</h1>
    </div>
    """, unsafe_allow_html=True)

with col4:
    outage_count = len(data.get('power_outages', []))
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
        <h3>Power Outages</h3>
        <h1>{outage_count}</h1>
    </div>
    """, unsafe_allow_html=True)

# Map Visualization
st.subheader("📍 Real-time Map")
col_map1, col_map2 = st.columns([2, 1])

with col_map1:
    # Create map centered on Nepal
    m = folium.Map(location=[28.3949, 84.1240], zoom_start=7)
    
    # Add earthquake markers
    for quake in data.get('earthquakes', []):
        mag = quake.get('magnitude', 0)
        depth = quake.get('depth', 0)
        
        # Color by magnitude
        if mag >= 5.0:
            color = 'red'
        elif mag >= 4.0:
            color = 'orange'
        else:
            color = 'green'
        
        folium.CircleMarker(
            location=[quake.get('latitude', 0), quake.get('longitude', 0)],
            radius=mag * 2,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"""
                <b>Earthquake</b><br>
                Magnitude: {mag}<br>
                Depth: {depth} km<br>
                Location: {quake.get('place', 'N/A')}<br>
                Time: {quake.get('time', 'N/A')}
            """
        ).add_to(m)
    
    # Add weather markers (Approx coords for cities for demo)
    city_coords = {
        "Kathmandu": [27.7172, 85.3240],
        "Pokhara": [28.2096, 83.9856],
        "Biratnagar": [26.4525, 87.2718],
        "Lalitpur": [27.6644, 85.3188],
        "Bharatpur": [27.6792, 84.4385]
    }
    
    for weather in data.get('weather', []):
        city = weather.get('city')
        if city in city_coords:
            coords = city_coords[city]
            folium.Marker(
                location=coords,
                icon=folium.Icon(color='blue', icon='cloud'),
                popup=f"""
                    <b>Weather: {city}</b><br>
                    Temp: {weather.get('temperature', 'N/A')}°C<br>
                    Conditions: {weather.get('condition', 'N/A')}
                """
            ).add_to(m)
    
    folium_static(m, width=900, height=500)

with col_map2:
    st.subheader("Legend")
    st.markdown("""
    - 🔴 Magnitude ≥ 5.0 (Severe)
    - 🟠 Magnitude 4.0-4.9 (Moderate)
    - 🟢 Magnitude < 4.0 (Minor)
    - 🔵 Weather Stations
    """)
    
    # Recent significant events
    st.subheader("Recent Events")
    for quake in data.get('earthquakes', [])[:3]:
        st.info(f"M{quake['magnitude']} - {quake.get('place', 'Unknown')}")

# Charts Section
st.subheader("📈 Analytics & Trends")

tab1, tab2, tab3 = st.tabs(["Earthquakes", "Weather", "Correlations"])

with tab1:
    if data.get('earthquakes'):
        df_quakes = pd.DataFrame(data['earthquakes'])
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Magnitude distribution
            fig = px.histogram(
                df_quakes, 
                x='magnitude',
                nbins=20,
                title="Earthquake Magnitude Distribution",
                labels={'magnitude': 'Magnitude', 'count': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_chart2:
            # Time series of earthquakes
            df_quakes['time'] = pd.to_datetime(df_quakes['time'])
            df_quakes['hour'] = df_quakes['time'].dt.floor('H')
            hourly_counts = df_quakes.groupby('hour').size().reset_index(name='count')
            
            fig = px.line(
                hourly_counts,
                x='hour',
                y='count',
                title="Earthquakes Per Hour",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    if data.get('weather'):
        df_weather = pd.DataFrame(data['weather'])
        
        col_weather1, col_weather2 = st.columns(2)
        
        with col_weather1:
            # Temperature by city
            latest_weather = df_weather.sort_values('time').groupby('city').last().reset_index()
            
            fig = px.bar(
                latest_weather,
                x='city',
                y='temperature',
                color='temperature',
                title="Current Temperatures by City",
                color_continuous_scale='RdYlBu_r'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_weather2:
            # Weather conditions pie chart
            condition_counts = df_weather['condition'].value_counts().reset_index()
            condition_counts.columns = ['condition', 'count']
            
            fig = px.pie(
                condition_counts,
                values='count',
                names='condition',
                title="Weather Conditions Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    if correlations.get('correlations'):
        st.subheader("Data Correlations & Insights")
        
        for corr in correlations['correlations']:
            with st.expander(f"🔍 {corr.get('type', 'Correlation').replace('_', ' ').title()}"):
                st.write(f"**Message**: {corr.get('message')}")
                st.write(f"**Confidence**: {corr.get('confidence', 'Unknown')}")
                
                if corr.get('districts'):
                    st.write("**Affected Districts**:")
                    cols = st.columns(3)
                    for i, district in enumerate(corr['districts']):
                        cols[i % 3].markdown(f"• {district}")
                
                if corr.get('recommendation'):
                    st.info(f"**Recommendation**: {corr['recommendation']}")
    
    # Additional insights
    if correlations.get('insights'):
        st.subheader("Statistical Insights")
        
        insights = correlations['insights']
        
        if insights.get('earthquake_frequency'):
            df_freq = pd.DataFrame(insights['earthquake_frequency'])
            fig = px.line(
                df_freq,
                x='hour',
                y='count',
                title="Earthquake Frequency (Last 24 Hours)"
            )
            st.plotly_chart(fig, use_container_width=True)

# Alerts Section
st.subheader("🚨 Active Alerts & Notifications")

if data.get('alerts'):
    alerts_df = pd.DataFrame(data['alerts'])
    
    for _, alert in alerts_df.iterrows():
        status = alert.get('status')
        if status == 'Danger':
            st.error(f"""
            **FLOOD ALERT: {alert.get('station')}**
            
            Water Level: {alert.get('water_level')}m (Danger Level: {alert.get('danger_level')}m)
            
            *Updated: {alert.get('time', 'Unknown')}*
            """)
        elif status == 'Warning':
            st.warning(f"""
            **FLOOD WARNING: {alert.get('station')}**
            
            Water Level: {alert.get('water_level')}m (Warning Level: {alert.get('warning_level')}m)
            """)
        else:
            st.info(f"""
            **Steady: {alert.get('station')}** - Level: {alert.get('water_level')}m
            """)

# Power Outages Section
if data.get('power_outages'):
    st.subheader("⚡ Power Outage Schedule")
    
    outages_df = pd.DataFrame(data['power_outages'])
    
    for district in outages_df['district'].unique():
        district_outages = outages_df[outages_df['district'] == district]
        
        with st.expander(f"{district} - {len(district_outages)} outage(s)"):
            for _, outage in district_outages.iterrows():
                st.write(f"**Schedule**: {outage.get('schedule', 'Unknown')}")
                st.write(f"**Duration**: {outage.get('outage_start')} to {outage.get('outage_end')}")

# Auto-refresh
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🇳🇵 Nepal Data Hub | Real-time Analytics Platform</p>
    <p>Data Sources: USGS Earthquakes • OpenWeather • Nepal Government APIs</p>
    <p>Built with Python, FastAPI, Kafka, PostgreSQL, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
