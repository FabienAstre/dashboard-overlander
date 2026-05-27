import streamlit as st
from components.map_view import render_map, TILESETS
from components.widgets import section_title, alert_row, metric_tile
from components.osm_places import (
    fetch_by_country, fetch_by_radius,
    geocode_place, filter_places, COUNTRIES
)

def render_map_intelligence():
    st.markdown("### 🌍 Map Intelligence")

    # ── Layer toggles ──
    tc1, tc2, tc3, tc4, tc5 = st.columns(5)
    with tc1: st.session_state.show_fuel    = st.toggle("⛽ Fuel",    value=st.session_state.show_fuel,    key="mi_f")
    with tc2: st.session_state.show_camps   = st.toggle("🏕 Camps",   value=st.session_state.show_camps,   key="mi_c")
    with tc3: st.session_state.show_borders = st.toggle("🛂 Borders", value=st.session_state.show_borders, key="mi_b")
    with tc4: st.session_state.show_safety  = st.toggle("🛡 Safety",  value=st.session_state.show_safety,  key="mi_s")
    with tc5:
        ts = list(TILESETS.keys())
        sel = st.selectbox("Style", ts,
                           index=ts.index(st.session_state.get("selected_tileset", "CartoDB Dark Matter")),
                           key="mi_ts", label_visibility="collapsed")
        st.session_state.selected_tileset = sel

    # ── OSM Data Source Controls ──
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_title("📡 OSM Data Source")

    mode = st.radio(
        "Fetch mode",
        ["By Country", "By Radius from Location"],
        horizontal=True,
        label_visibility="collapsed",
        key="osm_mode",
    )

    places = []

    if mode == "By Country":
        dc1, dc2 = st.columns([2, 1])
        with dc1:
            selected_countries = st.multiselect(
                "Countries",
                list(COUNTRIES.keys()),
                default=["Mexico"],
                label_visibility="collapsed",
                key="osm_countries",
            )
        with dc2:
            fetch_btn = st.button("🔄 Fetch OSM Data", use_container_width=True, key="fetch_country")

        if fetch_btn or st.session_state.get("osm_places_loaded"):
            with st.spinner("Fetching real OSM data..."):
                for country in selected_countries:
                    cc = COUNTRIES[country]
                    result = fetch_by_country(cc)
                    places.extend(result)
            st.session_state["osm_places"] = places
            st.session_state["osm_places_loaded"] = True

    else:
        rc1, rc2, rc3 = st.columns([3, 1, 1])
        with rc1:
            center_place = st.text_input(
                "Center location",
                value=st.session_state.get("origin", "Kamloops, BC"),
                label_visibility="collapsed",
                key="osm_center",
                placeholder="e.g. La Paz, Mexico",
            )
        with rc2:
            radius_km = st.number_input(
                "Radius km", min_value=10, max_value=500,
                value=200, step=25, key="osm_radius",
                label_visibility="collapsed",
            )
        with rc3:
            fetch_btn = st.button("🔄 Fetch", use_container_width=True, key="fetch_radius")

        if fetch_btn:
            with st.spinner("Geocoding " + center_place + "..."):
                coords = geocode_place(center_place)
            if coords:
                with st.spinner("Fetching OSM data within " + str(radius_km) + " km..."):
                    places = fetch_by_radius(coords[0], coords[1], radius_km)
                st.session_state["osm_places"] = places
                st.session_state["osm_places_loaded"] = True
                st.session_state["osm_radius_center"] = coords
            else:
                st.error("Could not geocode: " + center_place)

    # ── Stats row ──
    places = st.session_state.get("osm_places", [])
    if places:
        camps = filter_places(places, ["campsite"])
        fuel  = filter_places(places, ["fuel"])
        water = filter_places(places, ["water"])

        s1, s2, s3, s4 = st.columns(4)
        with s1: metric_tile(str(len(places)),  "TOTAL POIs",   "From OSM")
        with s2: metric_tile(str(len(camps)),   "CAMPSITES",    "Real locations")
        with s3: metric_tile(str(len(fuel)),    "FUEL STOPS",   "Real stations")
        with s4: metric_tile(str(len(water)),   "WATER POINTS", "Real sources")

        # Push to session for map to use
        st.session_state["osm_camps"] = camps
        st.session_state["osm_fuel"]  = fuel
        st.session_state["osm_water"] = water

    # ── Map ──
    render_map(height=500)

    # ── Bottom panels ──
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        section_title("🛡 Safety Zones")
        for level, loc, note in [
            ("🔴 HIGH",   "Tijuana border zone",          "Theft, verify insurance"),
            ("🟡 MEDIUM", "Guerrero Negro stretch",        "No services 300 km"),
            ("🔵 LOW",    "Portland corridor",             "Traffic congestion"),
        ]:
            st.markdown(
                '<div class="os-card" style="padding:0.55rem 0.8rem;margin-bottom:0.4rem;">'
                '<div style="font-size:0.8rem;font-weight:600;color:var(--text-primary);">' + level + " · " + loc + "</div>"
                '<div style="font-size:0.7rem;color:var(--text-muted);">' + note + "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

    with c2:
        section_title("⛽ Fuel Gap Analysis")
        tank_range = int(st.session_state.tank_capacity_l / st.session_state.consumption_l100 * 100)
        st.markdown(
            '<div class="os-card"><div style="font-size:0.75rem;color:var(--text-muted);">Tank range at full</div>'
            '<div style="font-family:Rajdhani,sans-serif;font-size:1.3rem;font-weight:700;color:var(--accent-cyan);">'
            + str(tank_range) + " km</div></div>",
            unsafe_allow_html=True,
        )
        for seg, km, ico in [
            ("LA → Ensenada",    210, "✅"),
            ("Ensenada → G.Negro", 490, "⚠️"),
            ("G.Negro → Loreto", 360, "✅"),
            ("Loreto → La Paz",  240, "✅"),
            ("La Paz → Cabo",    230, "✅"),
        ]:
            color = "var(--accent-red)" if km > tank_range * 0.85 else "var(--text-secondary)"
            st.markdown(
                '<div style="display:flex;justify-content:space-between;padding:0.35rem 0;'
                'border-bottom:1px solid var(--border);font-size:0.78rem;">'
                "<span>" + ico + " " + seg + "</span>"
                '<span style="color:' + color + ';">' + str(km) + " km</span></div>",
                unsafe_allow_html=True,
            )

    with c3:
        section_title("🏕 Camp Density")
        osm_camps = st.session_state.get("osm_camps", [])
        if osm_camps:
            from collections import Counter
            # rough region bucketing by lat
            regions = []
            for c in osm_camps:
                if c["lat"] > 49:   regions.append("BC Canada")
                elif c["lat"] > 46: regions.append("Washington")
                elif c["lat"] > 42: regions.append("Oregon")
                elif c["lat"] > 32: regions.append("California")
                else:               regions.append("Baja")
            counts = Counter(regions)
            for region, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                bar_w = min(95, int(count / max(counts.values()) * 90))
                st.markdown(
                    '<div style="margin-bottom:0.55rem;">'
                    '<div style="display:flex;justify-content:space-between;font-size:0.75rem;color:var(--text-secondary);">'
                    "<span>" + region + "</span>"
                    '<span style="color:var(--accent-green);">' + str(count) + " sites</span></div>"
                    '<div class="fuel-bar-track" style="margin-top:0.15rem;">'
                    '<div style="height:100%;width:' + str(bar_w) + '%;border-radius:4px;'
                    'background:var(--accent-green);opacity:0.7;"></div></div></div>',
                    unsafe_allow_html=True,
                )
        else:
            alert_row("ℹ️", "Fetch OSM data above to see camp density.", "info")
