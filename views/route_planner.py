import streamlit as st
from components.widgets import section_title, alert_row, route_score_bar, waypoint_list, metric_tile

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
    st.markdown("### Route Planner")

    left, right = st.columns([2, 1], gap="medium")

 with left:
    section_title("Route Setup")
    c1, c2 = st.columns(2)
    with c1:
        origin = st.text_input("Origin", value=s.origin, key="orig_i")
        if origin != s.origin:
            s.origin = origin
    with c2:
        destination = st.text_input("Destination", value=s.destination, key="dest_i")
        if destination != s.destination:
            s.destination = destination
    

        section_title("Waypoints")
        for i, wp in enumerate(s.waypoints):
            c1, c2 = st.columns([5, 1])
            with c1:
                s.waypoints[i] = st.text_input(
                    "Waypoint", value=wp, key="wp_" + str(i), label_visibility="collapsed"
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
        # Reset avoid_options to empty list to avoid default mismatch
        s.avoid_options = st.multiselect(
            "Avoid",
            AVOID_OPTIONS,
            default=[],
            label_visibility="collapsed",
        )

        if st.button("Calculate Route", use_container_width=True, type="primary"):
            import time
            time.sleep(0.8)
            scores = {
                "Safest": 81,
                "Fastest": 62,
                "Most Scenic": 74,
                "Off-Road Optimized": 68,
                "Fuel Efficient": 77,
            }
            s.route_safety_score = scores[s.route_mode]
            st.success("Route calculated — " + s.route_mode + " mode.")

    with right:
        section_title("Route Intelligence")
        metric_tile("3,850", "TOTAL KM", str(len(s.waypoints)) + " stops")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        metric_tile("~6.4", "DAYS", "at 600 km/day")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        metric_tile("$980", "EST. FUEL COST", "CAD approx.")
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
        section_title("Waypoint Summary")
        waypoint_list(s.waypoints[:4], s.origin, "...")
