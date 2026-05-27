import streamlit as st
from components.map_view import render_map
from components.widgets import (section_title, metric_tile, alert_row,
    safety_score_widget, route_score_bar, waypoint_list, campsite_card, fuel_stop_card)

def render_dashboard():
    s = st.session_state
    fuel_range = int(s.tank_capacity_l*(s.fuel_level_pct/100)/s.consumption_l100*100)
    service_due = max(0, s.last_service_km+s.service_interval_km-s.odometer_km)

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    with m1: metric_tile("3,850","ROUTE KM","Kamloops → Cabo")
    with m2: metric_tile(str(len(s.waypoints)),"WAYPOINTS","Along route")
    with m3: metric_tile(f"{s.fuel_level_pct}%","FUEL LEVEL",f"{int(s.tank_capacity_l*s.fuel_level_pct/100)}L",
                         "var(--accent-amber)" if s.fuel_level_pct<40 else "var(--accent-cyan)")
    with m4: metric_tile(str(fuel_range),"RANGE KM",f"At {s.consumption_l100}L/100km")
    with m5: metric_tile(str(s.route_safety_score),"SAFETY SCORE","Route average",
                         "var(--accent-green)" if s.route_safety_score>=80 else "var(--accent-amber)")
    with m6: metric_tile(f"{service_due:,}","SERVICE KM","Until next service",
                         "var(--accent-red)" if service_due<500 else "var(--accent-cyan)")

    st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)
    map_col, intel_col = st.columns([3,1], gap="small")

    with map_col:
        section_title("📡 Live Expedition Map")
        render_map(height=510)

    with intel_col:
        section_title("🛡 Route Safety")
        safety_score_widget(s.route_safety_score)
        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
        section_title("📊 Route Scores")
        route_score_bar("Safety",      74, "var(--accent-green)")
        route_score_bar("Road Quality",68, "var(--accent-cyan)")
        route_score_bar("Fuel Access", 82, "var(--accent-amber)")
        route_score_bar("Camping",     91, "var(--accent-green)")
        route_score_bar("Scenery",     95, "var(--accent-violet)")
        st.markdown("<div style='margin-top:0.5rem;'></div>", unsafe_allow_html=True)
        section_title("⚡ Active Alerts")
        alert_row("🛂","TIP required at Otay Mesa. Bring vehicle title.","warn")
        alert_row("⛽","Long fuel gap past Guerrero Negro — top up.","danger")
        alert_row("🌙","Avoid Tijuana border after 21:00.","warn")
        alert_row("✅","Manning Park open — good first night stop.","ok")

    st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)
    col_wp, col_fuel, col_camp = st.columns(3, gap="small")

    with col_wp:
        section_title("📍 Route Waypoints")
        waypoint_list(s.waypoints, s.origin, s.destination)
        st.markdown('<div style="margin-top:0.75rem;font-family:\'Rajdhani\',sans-serif;font-size:1.1rem;font-weight:700;color:var(--text-primary);">~6.5 days drive time</div>', unsafe_allow_html=True)

    with col_fuel:
        section_title("⛽ Fuel Stops En Route")
        for i,fs in enumerate(s.fuel_stops[:5]):
            fuel_stop_card(fs,i)

    with col_camp:
        section_title("🏕 Top Campsites")
        for c in sorted(s.campsites, key=lambda x:x["score"], reverse=True)[:5]:
            campsite_card(c)
