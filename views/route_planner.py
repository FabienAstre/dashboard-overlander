import streamlit as st
from components.widgets import section_title, alert_row, route_score_bar, waypoint_list, metric_tile
from components.map_view import fetch_route, geocode

ROUTE_MODES = ["Safest", "Fastest", "Most Scenic", "Off-Road Optimized", "Fuel Efficient"]

AVOID_OPTIONS = [
    "Night driving sections",
    "High-crime corridors",
    "Unpaved roads",
    "Highways over 80 km/h",
    "Toll roads",
    "Border wait over 1h",
]


def render_route_planner():
    s = st.session_state
    st.markdown("### 📍 Route Planner")
    st.markdown(
        '<p style="color:var(--text-secondary);margin-top:-0.5rem;margin-bottom:1rem;">'
        "Plan, score, and optimize your expedition route.</p>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([2, 1], gap="medium")

    with left:
        section_title("Route Setup")
        c1, c2 = st.columns(2)
        with c1:
            origin = st.text_input("Origin", value=s.origin, key="orig_i")
            if origin != s.origin:
                s.origin = origin
                fetch_route.clear()
                geocode.clear()
                if "live_weather" in st.session_state:
                    del st.session_state["live_weather"]
                st.rerun()
        with c2:
            destination = st.text_input("Destination", value=s.destination, key="dest_i")
            if destination != s.destination:
                s.destination = destination
                fetch_route.clear()
                geocode.clear()
                st.rerun()

        section_title("Waypoints")
        for i, wp in enumerate(s.waypoints):
            c1, c2 = st.columns([5, 1])
            with c1:
                s.waypoints[i] = st.text_input(
                    "Waypoint",
                    value=wp,
                    key="wp_" + str(i),
                    label_visibility="collapsed",
                )
            with c2:
                if st.button("X", key="del_" + str(i)):
                    s.waypoints.pop(i)
                    st.rerun()

        if st.button("Add Waypoint", use_container_width=True):
            s.waypoints.append("")
            st.rerun()

        section_title("Route Mode")
        if s.route_mode not in ROUTE_MODES:
            s.route_mode = ROUTE_MODES[0]
        s.route_mode = st.radio(
            "Mode",
            ROUTE_MODES,
            index=ROUTE_MODES.index(s.route_mode),
            horizontal=True,
            label_visibility="collapsed",
        )

        section_title("Avoid Options")
        s.avoid_options = st.multiselect(
            "Avoid",
            AVOID_OPTIONS,
            default=[],
            label_visibility="collapsed",
        )

        if st.button("Calculate Route", use_container_width=True, type="primary"):
            fetch_route.clear()
            geocode.clear()
            import time
            time.sleep(0.8)
            scores = {
                "Safest":             81,
                "Fastest":            62,
                "Most Scenic":        74,
                "Off-Road Optimized": 68,
                "Fuel Efficient":     77,
            }
            s.route_safety_score = scores[s.route_mode]
            st.success("Route calculated — " + s.route_mode + " mode.")

    with right:
        section_title("Route Intelligence")

        total_km   = 3850
        days_est   = round(total_km / 600, 1)
        fuel_total = int(total_km / 100 * s.consumption_l100)
        cost_est   = round(fuel_total * 1.55, 0)
        wp_count   = len([w for w in s.waypoints if w.strip()])

        metric_tile(
            str(total_km),
            "TOTAL KM",
            str(wp_count) + " waypoints",
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        metric_tile("~" + str(days_est), "DAYS", "at 600 km/day")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        metric_tile("$" + str(int(cost_est)), "EST. FUEL COST", "CAD approx.")
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        section_title("Route Scoring")
        scores = {
            "Safest":             (81, 55, 82, 91, 78),
            "Fastest":            (62, 90, 79, 55, 60),
            "Most Scenic":        (74, 65, 70, 95, 88),
            "Off-Road Optimized": (68, 58, 65, 90, 93),
            "Fuel Efficient":     (77, 72, 88, 80, 72),
        }
        sc = scores.get(s.route_mode, (74, 68, 82, 91, 95))
        route_score_bar("Safety",  sc[0], "var(--accent-green)")
        route_score_bar("Speed",   sc[1], "var(--accent-cyan)")
        route_score_bar("Fuel",    sc[2], "var(--accent-amber)")
        route_score_bar("Camping", sc[3], "var(--accent-green)")
        route_score_bar("Scenery", sc[4], "var(--accent-violet)")

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section_title("Route Alerts")
        alert_row("🛂", "2 border crossings detected.", "info")
        alert_row("⛽", "Remote gap: Guerrero Negro stretch.", "danger")
        alert_row("🌙", "Night driving not recommended after TJ.", "warn")
        alert_row("🏕", "10 campsites along route.", "ok")

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section_title("Current Route")
        st.markdown(
            '<div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:0.3rem;">'
            "From: <span style='color:var(--accent-cyan);'>" + s.origin + "</span></div>"
            '<div style="font-size:0.78rem;color:var(--text-secondary);">'
            "To: <span style='color:var(--accent-green);'>" + s.destination + "</span></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        waypoint_list(
            [w for w in s.waypoints if w.strip()][:4],
            s.origin,
            s.destination,
        )
