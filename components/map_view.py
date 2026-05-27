import streamlit as st
import folium
import requests
from streamlit_folium import st_folium
from components.osm_places import filter_places

TILESETS = {
    "CartoDB Dark Matter": {
        "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr":  "© OpenStreetMap, © CARTO",
    },
    "CartoDB Voyager": {
        "tiles": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        "attr":  "© OpenStreetMap, © CARTO",
    },
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr":  "© OpenStreetMap contributors",
    },
    "Esri Satellite": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr":  "Tiles © Esri",
    },
}

FALLBACK_COORDS = [
    [50.67, -120.33],
    [49.80, -119.50],
    [49.03, -119.46],
    [47.66, -117.43],
    [45.52, -122.68],
    [40.58, -122.38],
    [38.58, -121.49],
    [34.05, -118.24],
    [32.52, -117.04],
    [31.87, -116.60],
    [27.97, -114.06],
    [26.01, -111.34],
    [24.14, -110.31],
    [22.89, -109.92],
]


@st.cache_data(ttl=3600, show_spinner=False)
def geocode(place):
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "OverlanderOS/1.0"},
            timeout=5,
        )
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_route(origin, destination):
    o = geocode(origin)
    d = geocode(destination)
    if not o or not d:
        return FALLBACK_COORDS, FALLBACK_COORDS[0], FALLBACK_COORDS[-1]
    try:
        coords_str = (
            str(o[1]) + "," + str(o[0]) + ";"
            + str(d[1]) + "," + str(d[0])
        )
        url = "https://router.project-osrm.org/route/v1/driving/" + coords_str
        r = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson"},
            timeout=10,
        )
        data = r.json()
        if data.get("code") == "Ok":
            raw = data["routes"][0]["geometry"]["coordinates"]
            coords = [[lat, lon] for lon, lat in raw]
            return coords, o, d
    except Exception:
        pass
    return FALLBACK_COORDS, o if o else FALLBACK_COORDS[0], d if d else FALLBACK_COORDS[-1]


def _icon(emoji, size=22):
    return folium.DivIcon(
        html='<div style="font-size:' + str(size) + 'px;line-height:1;">' + emoji + "</div>",
        icon_size=(size + 4, size + 4),
        icon_anchor=(size // 2, size // 2),
    )


def build_expedition_map(center, zoom, tileset_name="CartoDB Dark Matter",
                         show_fuel=True, show_camps=True,
                         show_borders=True, show_safety=True):

    ts = TILESETS.get(tileset_name, TILESETS["CartoDB Dark Matter"])
    if ts["tiles"] == "OpenStreetMap":
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    else:
        m = folium.Map(location=center, zoom_start=zoom,
                       tiles=ts["tiles"], attr=ts["attr"])

    s = st.session_state

    # ── Route polyline ──
    route_coords, start, end = fetch_route(s.origin, s.destination)
    folium.PolyLine(
        route_coords,
        color="#00d4ff",
        weight=4,
        opacity=0.9,
        tooltip=s.origin.split(",")[0] + " to " + s.destination.split(",")[0],
    ).add_to(m)
    folium.PolyLine(route_coords, color="#00d4ff", weight=10, opacity=0.12).add_to(m)

    # ── Origin / Destination markers ──
    folium.Marker(start, icon=_icon("🟢", 26), tooltip="Origin: " + s.origin).add_to(m)
    folium.Marker(end,   icon=_icon("🏁", 26), tooltip="Destination: " + s.destination).add_to(m)

    # ── OSM places from session (loaded via Map Intelligence page) ──
    all_places = st.session_state.get("osm_places", [])

    # Campsites
    if show_camps:
        camps = filter_places(all_places, types=["campsite"])
        for c in camps[:400]:
            fee_txt = " · Free" if c["fee"] == "no" else (" · Fee" if c["fee"] == "yes" else "")
            folium.Marker(
                [c["lat"], c["lon"]],
                icon=_icon("🏕", 18),
                tooltip="<b>" + c["name"] + "</b>" + fee_txt,
            ).add_to(m)

    # Fuel stops
    if show_fuel:
        fuel = filter_places(all_places, types=["fuel"])
        for f in fuel[:400]:
            brand = (" · " + f["brand"]) if f["brand"] else ""
            folium.Marker(
                [f["lat"], f["lon"]],
                icon=_icon("⛽", 18),
                tooltip="<b>" + f["name"] + "</b>" + brand,
            ).add_to(m)

    # Water points
    water = filter_places(all_places, types=["water"])
    for w in water[:100]:
        folium.Marker(
            [w["lat"], w["lon"]],
            icon=_icon("💧", 16),
            tooltip="<b>" + w["name"] + "</b>",
        ).add_to(m)

    # ── Border crossings ──
    if show_borders:
        for bc in s.border_crossings:
            folium.Marker(
                [bc["lat"], bc["lon"]],
                icon=_icon("🛂", 22),
                tooltip=(
                    "<b>" + bc["name"] + "</b><br>"
                    + bc["country"] + "<br>"
                    + "Wait ~" + str(bc["wait_min"]) + " min"
                ),
            ).add_to(m)

    # ── Safety zones ──
    if show_safety:
        hazards = [
            {"lat": 32.6, "lon": -117.1, "label": "High theft risk — TJ border",  "level": "high"},
            {"lat": 27.9, "lon": -114.1, "label": "Remote — 300 km no services",  "level": "medium"},
            {"lat": 45.5, "lon": -122.7, "label": "Urban congestion",             "level": "low"},
        ]
        colors = {"high": "#ef4444", "medium": "#f59e0b", "low": "#3b82f6"}
        for hz in hazards:
            folium.Circle(
                [hz["lat"], hz["lon"]],
                radius=40000,
                color=colors[hz["level"]],
                fill=True,
                fill_color=colors[hz["level"]],
                fill_opacity=0.08,
                tooltip=hz["label"],
            ).add_to(m)

    return m


def render_map(height=520):
    s = st.session_state
    ts_options = list(TILESETS.keys())

    c1, c2 = st.columns([3, 1])
    with c1:
        sel = st.selectbox(
            "Style", ts_options,
            index=ts_options.index(s.get("selected_tileset", "CartoDB Dark Matter")),
            label_visibility="collapsed",
            key="map_ts",
        )
        st.session_state.selected_tileset = sel
    with c2:
        zoom = st.slider(
            "Zoom", 3, 14, s.map_zoom,
            label_visibility="collapsed",
            key="map_z",
        )
        st.session_state.map_zoom = zoom

    osm_loaded = st.session_state.get("osm_places_loaded", False)
    if not osm_loaded:
        st.markdown(
            '<div class="os-alert os-alert-info">💡 Go to <b>Map Intelligence</b> page and click <b>Fetch OSM Data</b> to load real campsites and fuel stops.</div>',
            unsafe_allow_html=True,
        )

    with st.spinner("Rendering map..."):
        m = build_expedition_map(
            s.map_center, zoom, sel,
            s.show_fuel, s.show_camps, s.show_borders, s.show_safety,
        )

    st_folium(m, width="100%", height=height, returned_objects=[])
