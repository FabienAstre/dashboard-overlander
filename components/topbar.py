import streamlit as st
from components.live_data import fetch_weather
from components.map_view import geocode


def render_topbar():
    s = st.session_state

    # ── Live weather — refresh when origin changes ──
    if (
        "live_weather" not in st.session_state
        or st.session_state.get("wx_origin") != s.origin
    ):
        coords = geocode(s.origin)
        if coords:
            fetch_weather.clear()
            wx = fetch_weather(coords[0], coords[1])
        else:
            wx = {"summary": "🌤 Weather unavailable"}
        st.session_state["live_weather"] = wx
        st.session_state["wx_origin"]    = s.origin

    wx = st.session_state["live_weather"]

    # ── Derived metrics ──
    fuel_range_km  = int(s.tank_capacity_l * (s.fuel_level_pct / 100) / s.consumption_l100 * 100)
    service_due_km = max(0, s.last_service_km + s.service_interval_km - s.odometer_km)

    # ── Badge classes ──
    online_class  = "os-badge-green" if s.online else "os-badge-red"
    online_label  = "🟢 ONLINE"      if s.online else "🔴 OFFLINE"
    safety_class  = "os-badge-green" if s.route_safety_score >= 80 else "os-badge-amber"
    service_class = "os-badge-red"   if service_due_km < 500 else "os-badge-amber"
    fuel_class    = "os-badge-red"   if fuel_range_km < 200 else "os-badge-cyan"

    # ── Layout ──
    col_title, col_badges, col_btn = st.columns([2, 9, 1])

    with col_title:
        st.markdown(
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;font-weight:700;'
            'color:var(--accent-cyan);letter-spacing:0.12em;padding:0.5rem 0 0.3rem 0;">'
            "⬡ OVERLANDER OS</div>",
            unsafe_allow_html=True,
        )

    with col_badges:
        st.markdown(
            '<div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;padding:0.4rem 0;">'

            # GPS
            '<span class="os-badge os-badge-green">🛰 GPS Active</span>'

            # Live weather
            '<span class="os-badge">' + wx["summary"] + "</span>"

            # Online status
            '<span class="os-badge ' + online_class + '">' + online_label + "</span>"

            # Fuel range
            '<span class="os-badge ' + fuel_class + '">⛽ ' + str(fuel_range_km) + " km range</span>"

            # Safety score
            '<span class="os-badge ' + safety_class + '">🛡 Safety ' + str(s.route_safety_score) + "/100</span>"

            # Service due
            '<span class="os-badge ' + service_class + '">🔧 Service in ' + str(service_due_km) + " km</span>"

            # Origin → Destination
            '<span class="os-badge os-badge-cyan" style="max-width:220px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">'
            "📍 " + s.origin.split(",")[0] + " → " + s.destination.split(",")[0] + "</span>"

            "</div>",
            unsafe_allow_html=True,
        )

    with col_btn:
        if st.button("⟳", key="wx_refresh", help="Refresh weather"):
            if "live_weather" in st.session_state:
                del st.session_state["live_weather"]
            if "wx_origin" in st.session_state:
                del st.session_state["wx_origin"]
            fetch_weather.clear()
            st.rerun()
