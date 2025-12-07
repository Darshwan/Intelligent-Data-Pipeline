import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import os
import time

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="Nepal Data Hub",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ULTRA-MINIMALIST CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    /* Global Reset */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
        background-color: #FAFAFA;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Layout Tweaks */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Typography */
    h1, h2, h3 {
        color: #111827;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 3rem;
        font-weight: 400;
    }

    /* Minimal Cards */
    div.metric-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: left;
        border: 1px solid #F3F4F6;
        transition: transform 0.2s;
    }
    
    div.metric-card:hover {
         transform: translateY(-2px);
         box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 600;
        color: #111827;
        line-height: 1.2;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6B7280;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        padding: 4px 8px;
        border-radius: 99px;
        background: #F3F4F6;
        color: #4B5563;
        display: inline-block;
        margin-top: 12px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #6B7280;
        font-size: 14px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB;
        border-bottom: 2px solid #2563EB;
    }

</style>
""", unsafe_allow_html=True)

# Main Layout
st.markdown('<div class="hero-title">Nepal Data Hub</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Real-time intelligence for disaster resilience.</div>', unsafe_allow_html=True)

# Fetch Data
@st.cache_data(ttl=60)
def fetch_data():
    try:
        resp = requests.get(f"{API_URL}/api/v1/dashboard", timeout=3)
        return resp.json() if resp.status_code == 200 else {}
    except:
        return {}

data = fetch_data()

if not data:
    st.warning("Connecting to source...")
    time.sleep(1)
    st.rerun()

# 1. KPI Grid (Minimal)
c1, c2, c3, c4 = st.columns(4)

with c1:
    count = len(data.get('earthquakes', []))
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Seismic Events</div>
        <div class="metric-value">{count}</div>
        <span class="metric-delta">Last 24h</span>
    </div>
    """, unsafe_allow_html=True)

with c2:
    w_count = data.get('dashboard_stats', {}).get('weather_updates', {}).get('count', 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Weather Nodes</div>
        <div class="metric-value">{w_count}</div>
        <span class="metric-delta">Active</span>
    </div>
    """, unsafe_allow_html=True)

with c3:
    alerts = len(data.get('alerts', []))
    color = "#EF4444" if alerts > 0 else "#10B981"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Flood Alerts</div>
        <div class="metric-value" style="color: {color}">{alerts}</div>
        <span class="metric-delta">Real-time</span>
    </div>
    """, unsafe_allow_html=True)

with c4:
    outages = len(data.get('power_outages', []))
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Grid Status</div>
        <div class="metric-value">{outages}</div>
        <span class="metric-delta">Outages</span>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Spacer

# 2. Main Content
t1, t2, t3 = st.tabs(["Overview", "Analytics", "Live Feed"])

with t1:
    col_map, col_list = st.columns([2.5, 1])
    
    with col_map:
        st.caption("GEOSPATIAL MONITOR")
        # Map with Minimal Tiles
        m = folium.Map(location=[28.3949, 84.1240], zoom_start=7, tiles="CartoDB positron")
        
        # Earthquakes (Minimal Circles)
        for q in data.get('earthquakes', []):
            mag = q.get('magnitude', 0)
            color = "#EF4444" if mag >= 5 else "#F59E0B" if mag >= 4 else "#3B82F6"
            folium.CircleMarker(
                [q['latitude'], q['longitude']],
                radius=mag*1.5, color=None, fill=True, fill_color=color, fill_opacity=0.6,
                popup=f"M{mag}"
            ).add_to(m)
        
        # Weather Markers (Dot style)
        city_coords = {
            "Kathmandu": [27.7172, 85.3240], "Pokhara": [28.2096, 83.9856],
            "Biratnagar": [26.4525, 87.2718], "Lalitpur": [27.6644, 85.3188]
        }
        for w in data.get('weather', []):
            if w.get('city') in city_coords:
                folium.CircleMarker(
                    city_coords[w['city']],
                    radius=3, color='#6B7280', fill=True, fill_opacity=0.8,
                    popup=f"{w['city']}: {w['temperature']}°C"
                ).add_to(m)

        folium_static(m, width=800, height=450)
        
    with col_list:
        st.caption("RECENT ACTIVITY")
        # Custom clean list
        for q in data.get('earthquakes', [])[:6]:
            mag = q.get('magnitude', 0)
            color = "🔴" if mag >= 5 else "🟠" if mag >= 4 else "🔵"
            st.markdown(f"""
            <div style="padding: 12px 0; border-bottom: 1px solid #f3f4f6;">
                <div style="font-weight: 500; font-size: 0.9rem;">{color} M{mag} Earthquake</div>
                <div style="font-size: 0.8rem; color: #6B7280;">{q.get('place')}</div>
                <div style="font-size: 0.75rem; color: #9CA3AF;">{q.get('time', '').split('T')[1][:5]} UTC</div>
            </div>
            """, unsafe_allow_html=True)

with t2:
    c_left, c_right = st.columns(2)
    
    with c_left:
        st.caption("SEISMIC INTENSITY")
        if data.get('earthquakes'):
            df = pd.DataFrame(data['earthquakes'])
            fig = px.histogram(df, x='magnitude', nbins=15, 
                             template="plotly_white", height=300)
            fig.update_traces(marker_color='#3B82F6')
            fig.update_layout(
                margin=dict(l=0,r=0,t=0,b=0), 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Magnitude",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
            
    with c_right:
        st.caption("TEMPERATURE SPREAD")
        if data.get('weather'):
            df = pd.DataFrame(data['weather'])
            fig = px.bar(df, x='city', y='temperature', 
                       template="plotly_white", height=300)
            fig.update_traces(marker_color='#10B981')
            fig.update_layout(
                margin=dict(l=0,r=0,t=0,b=0), 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title=None,
                yaxis_title="Temp (°C)"
            )
            st.plotly_chart(fig, use_container_width=True)

with t3:
    if data.get('alerts'):
        for alert in data['alerts']:
            status = alert.get('status')
            bg = "#FEF2F2" if status == 'Danger' else "#FFFBEB"
            border = "#F87171" if status == 'Danger' else "#FBBF24"
            st.markdown(f"""
            <div style="background: {bg}; border-left: 4px solid {border}; padding: 16px; border-radius: 4px; margin-bottom: 12px;">
                <div style="font-weight: 600; color: #111827;">{status.upper()}: {alert.get('station')}</div>
                <div style="font-size: 0.9rem;">Water Level: {alert.get('water_level')}m</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("System Normal. No active alerts.")

# Sidebar Controls
with st.sidebar:
    st.header("Settings")
    st.checkbox("Auto-refresh", value=True)
    st.select_slider("Range", options=["1h", "24h", "7d"], value="24h")

# Auto-refresh logic
time.sleep(60)
st.rerun()
