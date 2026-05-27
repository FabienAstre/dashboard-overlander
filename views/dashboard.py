import math
import streamlit as st
from components.map_view import render_map, fetch_route
from components.widgets import (
    section_title, metric_tile, alert_row,
    safety_score_widget, route_score_bar,
    waypoint_list, campsite_card, fuel_stop_card,
)


def haversine(lat1, lon1, lat2, lon2):
    R    = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a    = (math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def calc_route_km(route_coords):
    total = 0
    for i in range(len(route_coords) - 1):
        total += haversine(
            route_coords[i][0],     route_coords[i][1],
            route_coords[i + 1][0], route_coords[i + 1][1],
        )
    return int(total)


def render_dashboard():
    s = st.session_state

    # ── Real route distance from OSRM ──
    route_coords, start, end = fetch_route(s.origin, s.destination)
    total_km = calc_route_km(route_coords)

    # ── Derived metrics ──
    fuel_range   = int(s.tank_capacity_l * (s.fuel_level_pct / 100) / s.consumption_l100 * 100)
    service_due  = max(0, s.last_service_km + s.service_interval_km - s.odometer_km)
    wp_count     = len([w for w in s.waypoints if w.strip()])
    days_est     = round(total_km / 600, 1)
    fuel_total_l = int(total_km / 100 * s.consumption_l100)
    origin_short = s.origin.split(",")[0]
    dest_short   = s.destination.split(",")[0]

    # ── Top metrics row ──
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        metric_tile(
            str(total_km) + " km",
            "ROUTE DISTANCE",
            origin_short + " → " + dest_short,
        )
    with m2:
        metric_tile(
            str(wp_count),
            "WAYPOINTS",
            "Along route",
        )
    with m3:
        metric_tile(
            str(s.fuel_level_pct) + "%",
            "FUEL LEVEL",
            str(int(s.tank_capacity_l * s.fuel_level_pct / 100)) + "L in tank",
            "var(--accent-red)"   if s.fuel_level_pct < 25 else
            "var(--accent-amber)" if s.fuel_level_pct < 50 else
            "var(--accent-cyan)",
        )
    with m4:
        metric_tile(
            str(fuel_range) + " km",
            "CURRENT RANGE",
            "At " + str(s.consumption_l100) + "L/100km",
            "var(--accent-red)" if fuel_range < 200 else "var(--accent-cyan)",
        )
    with m5:
        metric_tile(
            str(s.route_safety_score) + "/100",
            "SAFETY SCORE",
            "Route average",
            "var(--accent-green)" if s.route_safety_score >= 80 else
            "var(--accent-amber)" if s.route_safety_score >= 60 else
            "var(--accent-red)",
        )
    with m6:
        metric_tile(
            str(service_due) + " km",
            "NEXT SERVICE",
            "Until due",
            "var(--accent-red)"   if service_due < 500  else
            "var(--accent-amber)" if service_due < 2000 else
            "var(--accent-cyan)",
        )

    st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)

    # ── Map + Intel panel ──
    map_col, intel_col = st.columns([3, 1], gap="small")

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
        alert_row("🛂", "TIP required at Otay Mesa. Bring vehicle title.", "warn")
        alert_row("⛽", "Long fuel gap past Guerrero Negro — top up.", "danger")
        alert_row("🌙", "Avoid Tijuana border after 21:00.", "warn")
        alert_row("✅", "Manning Park open — good first night stop.", "ok")

    st.markdown("<div style='margin:0.75rem 0;'></div>", unsafe_allow_html=True)

    # ── Bottom row ──
    col_wp, col_fuel, col_camp = st.columns(3, gap="small")

    with col_wp:
        section_title("📍 Route Waypoints")
        waypoint_list(
            [w for w in s.waypoints if w.strip()],
            s.origin,
            s.destination,
        )
        st.markdown(
            "<div style='margin-top:0.75rem;'>"
            "<div style='font-size:0.72rem;color:var(--text-muted);'>Est. at 600 km/day</div>"
            "<div style='font-family:Rajdhani,sans-serif;font-size:1.2rem;font-weight:700;"
            "color:var(--text-primary);'>~" + str(days_est) + " days</div>"
            "<div style='font-size:0.72rem;color:var(--text-muted);margin-top:0.2rem;'>"
            + str(total_km) + " km · "
            + str(fuel_total_l) + "L fuel est. · "
            + str(wp_count) + " stops"
            + "</div></div>",
            unsafe_allow_html=True,
        )

    with col_fuel:
        section_title("⛽ Fuel Stops En Route")
        for i, fs in enumerate(s.fuel_stops[:5]):
            fuel_stop_card(fs, i)

    with col_camp:
        section_title("🏕 Top Campsites")
        top_camps = sorted(s.campsites, key=lambda x: x["score"], reverse=True)[:5]
        for c in top_camps:
            campsite_card(c)
