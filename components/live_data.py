import requests
import streamlit as st


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather(lat, lon):
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude":  lat,
                "longitude": lon,
                "current":   "temperature_2m,weathercode,windspeed_10m",
                "timezone":  "auto",
            },
            timeout=8,
        )
        r.raise_for_status()
        data    = r.json()
        current = data.get("current", {})
        temp    = current.get("temperature_2m", "?")
        code    = current.get("weathercode", 0)
        wind    = current.get("windspeed_10m", 0)

        WX_CODES = {
            0:  ("☀️", "Clear"),
            1:  ("🌤", "Mostly Clear"),
            2:  ("⛅", "Partly Cloudy"),
            3:  ("☁️", "Overcast"),
            45: ("🌫", "Fog"),
            48: ("🌫", "Fog"),
            51: ("🌦", "Drizzle"),
            53: ("🌦", "Drizzle"),
            55: ("🌦", "Drizzle"),
            61: ("🌧", "Rain"),
            63: ("🌧", "Rain"),
            65: ("🌧", "Heavy Rain"),
            71: ("🌨", "Snow"),
            73: ("🌨", "Snow"),
            75: ("❄️", "Heavy Snow"),
            80: ("🌦", "Showers"),
            81: ("🌧", "Showers"),
            82: ("⛈", "Heavy Showers"),
            95: ("⛈", "Thunderstorm"),
            99: ("⛈", "Thunderstorm"),
        }
        icon, desc = WX_CODES.get(code, ("🌤", "Unknown"))
        return {
            "summary": icon + " " + desc + " · " + str(round(temp)) + "°C",
            "temp":    temp,
            "wind":    wind,
            "code":    code,
        }
    except Exception:
        return {
            "summary": "🌤 Weather unavailable",
            "temp":    None,
            "wind":    None,
            "code":    0,
        }


@st.cache_data(ttl=900, show_spinner=False)
def fetch_border_waits():
    try:
        r = requests.get(
            "https://bwt.cbp.gov/api/bwtdata",
            timeout=10,
            headers={"User-Agent": "OverlanderOS/1.0"},
        )
        r.raise_for_status()
        ports = {}
        for entry in r.json().get("bwt", []):
            port_name = entry.get("port_name", "")
            crossing  = entry.get("crossing_name", "")
            standard  = entry.get("standard_lane_wait_time", "N/A")
            ports[port_name + " " + crossing] = standard
        return ports
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_live_exchange_rates():
    try:
        r = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=8,
        )
        r.raise_for_status()
        rates = r.json().get("rates", {})
        return {
            "USD_CAD": rates.get("CAD", 1.36),
            "USD_MXN": rates.get("MXN", 17.2),
            "CAD_MXN": rates.get("MXN", 17.2) / rates.get("CAD", 1.36),
        }
    except Exception:
        return {
            "USD_CAD": 1.36,
            "USD_MXN": 17.2,
            "CAD_MXN": 12.6,
        }
