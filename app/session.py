import streamlit as st
from datetime import datetime

DEFAULTS = {
    "trip_name":        "Expedition Alpha",
    "trip_start_date":  datetime(2026, 6, 15),
    "trip_active":      True,
    "origin":           "Kamloops, BC, Canada",
    "destination":      "Cabo San Lucas, Mexico",
    "waypoints":        ["Kelowna, BC", "Spokane, WA", "Portland, OR", "Sacramento, CA", "Los Angeles, CA", "Ensenada, Mexico"],
    "route_mode":       "Safest",
    "avoid_options":    ["Highways > 80 km/h", "Unpaved at night"],
    "route_polyline":   None,
    "vehicle_name":     "Beast — Ford E350 7.3L",
    "tank_capacity_l":  150,
    "fuel_level_pct":   72,
    "consumption_l100": 16.5,
    "odometer_km":      214380,
    "last_service_km":  210000,
    "service_interval_km": 8000,
    "maint_notes":      [],
    "ai_messages":      [],
    "map_center":       [34.0, -116.0],
    "map_zoom":         5,
    "show_fuel":        True,
    "show_camps":       True,
    "show_borders":     True,
    "show_safety":      True,
    "selected_tileset": "CartoDB Dark Matter",
    "route_safety_score": 74,
    "fuel_stops": [
        {"name": "Osoyoos Shell",        "lat": 49.03, "lon": -119.46, "price": 1.82, "dist_km": 165},
        {"name": "Spokane Loves",        "lat": 47.66, "lon": -117.43, "price": 1.19, "dist_km": 390},
        {"name": "Portland TA",          "lat": 45.52, "lon": -122.68, "price": 1.29, "dist_km": 830},
        {"name": "Redding Pilot",        "lat": 40.58, "lon": -122.38, "price": 1.45, "dist_km": 1210},
        {"name": "Barstow Flying J",     "lat": 34.89, "lon": -117.02, "price": 1.38, "dist_km": 1740},
        {"name": "El Centro Chevron",    "lat": 32.79, "lon": -115.56, "price": 1.41, "dist_km": 1950},
        {"name": "Ensenada PEMEX",       "lat": 31.87, "lon": -116.60, "price": 23.8, "dist_km": 2180},
        {"name": "Guerrero Negro PEMEX", "lat": 27.97, "lon": -114.06, "price": 22.9, "dist_km": 2680},
        {"name": "Loreto PEMEX",         "lat": 26.01, "lon": -111.34, "price": 23.1, "dist_km": 3040},
        {"name": "La Paz PEMEX",         "lat": 24.14, "lon": -110.31, "price": 22.7, "dist_km": 3280},
    ],
    "campsites": [
        {"name": "Manning Park",       "lat": 49.07, "lon": -120.76, "type": "Provincial", "score": 88},
        {"name": "Okanagan Lake SP",   "lat": 49.80, "lon": -119.58, "type": "State Park",  "score": 82},
        {"name": "Colville NF",        "lat": 48.58, "lon": -118.39, "type": "Free/BLM",    "score": 79},
        {"name": "Mt Hood NF",         "lat": 45.32, "lon": -121.72, "type": "National F",  "score": 91},
        {"name": "Shasta NF",          "lat": 41.31, "lon": -122.31, "type": "National F",  "score": 85},
        {"name": "Mojave Dispersed",   "lat": 35.10, "lon": -115.48, "type": "Free/BLM",    "score": 77},
        {"name": "El Rosario Camp",    "lat": 30.06, "lon": -115.74, "type": "Palapa Camp", "score": 83},
        {"name": "Bahía Concepción",   "lat": 26.73, "lon": -111.88, "type": "Beach Camp",  "score": 96},
        {"name": "Agua Verde",         "lat": 25.51, "lon": -111.08, "type": "Remote Bay",  "score": 94},
        {"name": "Los Barriles Beach", "lat": 23.69, "lon": -109.69, "type": "Beach Camp",  "score": 89},
    ],
    "border_crossings": [
        {"name": "Osoyoos / Oroville",  "lat": 49.00, "lon": -119.44, "country": "CAN→USA",
         "doc": "Passport, NEXUS", "wait_min": 15, "status": "Normal"},
        {"name": "Otay Mesa / Tijuana", "lat": 32.55, "lon": -117.05, "country": "USA→MEX",
         "doc": "Passport, FMM, TIP", "wait_min": 45, "status": "Moderate"},
    ],
    "online":          True,
    "gps_fix":         "3D Fix — 8 sats",
    "weather_summary": "Partly Cloudy · 22°C",
}

def init_session_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value
