import streamlit as st
import folium
from streamlit_folium import st_folium
from components.discoveries import (
    fetch_discoveries_by_country,
    fetch_discoveries_by_radius,
    fetch_atlas_obscura_rss,
    fetch_wikipedia_nearby,
    filter_discoveries,
    TYPE_META,
)
from components.osm_places import geocode_place, COUNTRIES
from components.widgets import section_title, metric_tile, alert_row
from components.map_view import TILESETS, geocode

FILTER_TYPES = {
    "👁 Scenic Viewpoint":   "viewpoint",
    "🏖 Beach":              "beach",
    "♨️ Hot Spring":         "hot_spring",
    "💧 Waterfall":          "waterfall",
    "🏔 Summit":             "peak",
    "🗿 Ruins":              "ruins",
    "🗿 Archaeological":     "archaeological_site",
    "🏛 Attraction":         "attraction",
    "🏛 Museum":             "museum",
    "🎨 Artwork":            "artwork",
    "🌿 Nature Reserve":     "nature_reserve",
    "🏛 Monument":           "monument",
}


def render_discoveries():
    st.markdown("### 🔭 Discoveries")
    st.markdown(
        '<p style="color:var(--text-secondary);margin-top:-0.5rem;margin-bottom:1rem;">'
        "Tourist sites, scenic viewpoints, off-the-beaten-path gems and hidden places along your route.</p>",
        unsafe_allow_html=True,
    )

    # ── Fetch controls ──
    section_title("📡 Data Source")
    mode = st.radio(
        "Mode",
        ["By Country", "By Radius from Location"],
        horizontal=True,
        label_visibility="collapsed",
        key="disc_mode",
    )

    places = st.session_state.get("discovery_places", [])

    if mode == "By Country":
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            selected = st.multiselect(
                "Countries",
                list(COUNTRIES.keys()),
                default=["Mexico"],
                label_visibility="collapsed",
                key="disc_countries",
            )
        with dc2:
            fetch_btn = st.button("🔭 Fetch", use_container_width=True, key="disc_fetch_country")

        if fetch_btn:
            all_places = []
            for country in selected:
                cc = COUNTRIES[country]
                with st.spinner("Fetching discoveries in " + country + "..."):
                    result = fetch_discoveries_by_country(cc)
                    all_places.extend(result)
            st.session_state["discovery_places"] = all_places
            places = all_places
            st.success("Found " + str(len(places)) + " discoveries.")

    else:
        rc1, rc2, rc3 = st.columns([3, 1, 1])
        with rc1:
            center_place = st.text_input(
                "Center",
                value=st.session_state.get("origin", "La Paz, Mexico"),
                label_visibility="collapsed",
                placeholder="e.g. Loreto, Mexico",
                key="disc_center",
            )
        with rc2:
            radius_km = st.number_input(
                "Radius km", 10, 500, 150, 25,
                label_visibility="collapsed",
                key="disc_radius",
            )
        with rc3:
            fetch_btn = st.button("🔭 Fetch", use_container_width=True, key="disc_fetch_radius")

        if fetch_btn:
            with st.spinner("Geocoding " + center_place + "..."):
                coords = geocode_place(center_place)
            if coords:
                with st.spinner("Fetching discoveries within " + str(radius_km) + " km..."):
                    places = fetch_discoveries_by_radius(coords[0], coords[1], radius_km)
                st.session_state["discovery_places"] = places
                st.success("Found " + str(len(places)) + " discoveries.")
            else:
                st.error("Could not geocode: " + center_place)

    # ── Type filters ──
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_title("🎛 Filter by Type")
    selected_types = st.multiselect(
        "Types",
        list(FILTER_TYPES.keys()),
        default=list(FILTER_TYPES.keys()),
        label_visibility="collapsed",
        key="disc_type_filter",
    )
    active_types = [FILTER_TYPES[t] for t in selected_types]
    filtered = filter_discoveries(places, types=active_types if active_types else None)

    # ── Metrics ──
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    if filtered:
        type_counts = {}
        for p in filtered:
            type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1: metric_tile(str(len(filtered)),                          "TOTAL FOUND",   "After filters")
        with m2: metric_tile(str(type_counts.get("viewpoint", 0)),        "VIEWPOINTS",    "Scenic overlooks")
        with m3: metric_tile(str(type_counts.get("beach", 0)),            "BEACHES",       "Coastal spots")
        with m4: metric_tile(str(type_counts.get("hot_spring", 0) +
                                  type_counts.get("waterfall", 0)),       "NATURAL",       "Springs & falls")
        with m5: metric_tile(str(type_counts.get("ruins", 0) +
                                  type_counts.get("archaeological_site", 0)), "ANCIENT",   "Ruins & sites")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    # ── Main layout ──
    map_col, side_col = st.columns([3, 1], gap="small")

    with map_col:
        section_title("🗺️ Discoveries Map")

        # Build map
        ts_list = list(TILESETS.keys())
        sel_ts  = st.selectbox(
            "Style", ts_list,
            index=ts_list.index(st.session_state.get("selected_tileset", "CartoDB Dark Matter")),
            label_visibility="collapsed",
            key="disc_ts",
        )
        ts = TILESETS[sel_ts]
        if ts["tiles"] == "OpenStreetMap":
            m = folium.Map(location=st.session_state.map_center, zoom_start=6, tiles="OpenStreetMap")
        else:
            m = folium.Map(location=st.session_state.map_center, zoom_start=6,
                           tiles=ts["tiles"], attr=ts["attr"])

        # Plot discoveries
        for p in filtered[:500]:
            folium.Marker(
                [p["lat"], p["lon"]],
                icon=folium.DivIcon(
                    html='<div style="font-size:20px;line-height:1;">' + p["icon"] + "</div>",
                    icon_size=(28, 28),
                    icon_anchor=(14, 14),
                ),
                tooltip=(
                    "<b>" + p["icon"] + " " + p["name"] + "</b><br>"
                    + p["label"]
                    + ("<br><i>" + p["desc"][:100] + "...</i>" if p["desc"] else "")
                ),
            ).add_to(m)

        st_folium(m, width="100%", height=520, returned_objects=[])

    with side_col:
        # ── Atlas Obscura feed ──
        section_title("💀 Atlas Obscura")
        with st.spinner("Loading Atlas Obscura..."):
            ao_places = fetch_atlas_obscura_rss()

        if ao_places:
            for item in ao_places[:8]:
                st.markdown(
                    '<div class="os-card" style="padding:0.6rem 0.8rem;margin-bottom:0.4rem;">'
                    '<div style="font-size:0.82rem;font-weight:600;color:var(--text-primary);">'
                    + item["title"] + "</div>"
                    '<div style="font-size:0.7rem;color:var(--text-muted);margin-top:0.2rem;">'
                    + item["desc"][:120] + "...</div>"
                    '<a href="' + item["link"] + '" target="_blank" '
                    'style="font-size:0.68rem;color:var(--accent-cyan);">Read more →</a>'
                    "</div>",
                    unsafe_allow_html=True,
                )
        else:
            alert_row("ℹ️", "Atlas Obscura feed unavailable.", "info")

        # ── Wikipedia nearby ──
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section_title("📖 Wikipedia Nearby")
        s = st.session_state
        origin_coords = geocode(s.origin)
        if origin_coords:
            with st.spinner("Fetching Wikipedia POIs..."):
                wiki = fetch_wikipedia_nearby(origin_coords[0], origin_coords[1], 100)
            for w in wiki[:8]:
                dist_km = round(w["dist"] / 1000, 1)
                st.markdown(
                    '<div style="padding:0.4rem 0;border-bottom:1px solid var(--border);">'
                    '<div style="font-size:0.8rem;color:var(--text-primary);">' + w["name"] + "</div>"
                    '<div style="display:flex;justify-content:space-between;">'
                    '<span style="font-size:0.68rem;color:var(--text-muted);">' + str(dist_km) + " km away</span>"
                    '<a href="' + w["url"] + '" target="_blank" '
                    'style="font-size:0.68rem;color:var(--accent-cyan);">Wiki →</a>'
                    "</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            alert_row("ℹ️", "Set your origin to load Wikipedia POIs.", "info")

        # ── Place list ──
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section_title("📋 Place List (" + str(len(filtered)) + ")")
        if not filtered:
            alert_row("ℹ️", "Fetch data above to see places.", "info")
        for p in filtered[:20]:
            st.markdown(
                '<div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0;'
                'border-bottom:1px solid var(--border);">'
                '<span style="font-size:1rem;">' + p["icon"] + "</span>"
                '<div>'
                '<div style="font-size:0.78rem;color:var(--text-primary);">' + p["name"] + "</div>"
                '<div style="font-size:0.65rem;color:var(--text-muted);">' + p["label"] + "</div>"
                "</div></div>",
                unsafe_allow_html=True,
            )
        if len(filtered) > 20:
            st.markdown(
                '<div style="font-size:0.72rem;color:var(--text-muted);text-align:center;padding:0.5rem;">'
                "+ " + str(len(filtered) - 20) + " more on map</div>",
                unsafe_allow_html=True,
            )
