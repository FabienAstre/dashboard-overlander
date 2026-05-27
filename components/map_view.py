import streamlit as st
import folium
import requests
from streamlit_folium import st_folium

TILESETS = {
    "CartoDB Dark Matter": {
        "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap, © CARTO",
    },
    "CartoDB Voyager": {
        "tiles": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap, © CARTO",
    },
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors",
    },
    "Esri Satellite": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Tiles © Esri",
    },
}

# Fallback straight-line coords if OSRM fails
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


def get_route_coords(waypoints_lonlat):
    try:
        coords_str = ";".join(str(lon) + "," + str(lat) for lat, lon in waypoints_lonlat)
        url = "https://router.project-osrm.org/route/v1/driving/" + coords_str
        params = {"overview": "full", "geometries": "geojson", "steps": "false"}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("code") == "Ok":
            coords = data["routes"][0]["geometry"]["coordinates"]
            return [[lat, lon] for lon, lat in coords]
    except Exception:
        pass
    return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_route(waypoints_tuple):
    return get_route_coords(list(waypoints_tuple))


def _icon(emoji, size=24):
    return folium.DivIcon(
        html='<div style="font-size:' + str(size) + 'px;">' + emoji + "</div>",
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
        m = folium.Map(location=center, zoom_start=zoom, tiles=ts["tiles"], attr=ts["attr"])

    # Build waypoint list for OSRM: origin + waypoints + destination
    s = st.session_state
    all_points = []

    # Try to geocode origin and destination using Nominatim
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

    origin_coords = geocode(s.origin)
    dest_coords   = geocode(s.destination)

    if origin_coords and dest_coords:
        all_points = [origin_coords] + [origin_coords] + [dest_coords]
        # Use OSRM for road-following route
        route_key = tuple([origin_coords] + [dest_coords])
        road_coords = fetch_route(route_key)
        if road_coords:
            route_coords = road_coords
        else:
            route_coords = FALLBACK_COORDS
        start_coord = origin_coords
        end_coord   = dest_coords
    else:
        route_coords = FALLBACK_COORDS
        start_coord  = FALLBACK_COORDS[0]
        end_coord    = FALLBACK_COORDS[-1]

    # Draw route
    folium.PolyLine(route_coords, color="#00d4ff", weight=4, opacity=0.9,
                    tooltip="Route: " + s.origin.split(",")[0] + " to " + s.destination.split(",")[0]).add_to(m)
    folium.PolyLine(route_coords, color="#00d4ff", weight=10, opacity=0.12).add_to(m)

    # Origin / destination markers
    folium.Marker(start_coord, icon=_icon("🟢"), tooltip="Origin: " + s.origin).add_to(m)
    folium.Marker(end_coord,   icon=_icon("🏁"), tooltip="Destination: " + s.destination).add_to(m)

    # Fuel stops
    if show_fuel:
        for fs in s.fuel_stops:
            folium.Marker(
                [fs["lat"], fs["lon"]],
                icon=_icon("⛽", 20),
                tooltip="<b>" + fs["name"] + "</b><br>km " + str(fs["dist_km"]),
            ).add_to(m)

    # Campsites
    if show_camps:
        for c in s.campsites:
            folium.Marker(
                [c["lat"], c["lon"]],
                icon=_icon("🏕", 20),
                tooltip="<b>" + c["name"] + "</b><br>" + c["type"] + " - Score " + str(c["score"]),
            ).add_to(m)

    # Border crossings
    if show_borders:
        for bc in s.border_crossings:
            folium.Marker(
                [bc["lat"], bc["lon"]],
                icon=_icon("🛂", 22),
                tooltip="<b>" + bc["name"] + "</b><br>" + bc["country"] + "<br>Wait ~" + str(bc["wait_min"]) + " min",
            ).add_to(m)

    # Safety zones
    if show_safety:
        hazards = [
            {"lat": 32.6,  "lon": -117.1, "label": "High theft risk — TJ border",    "level": "high"},
            {"lat": 27.9,  "lon": -114.1, "label": "Remote — 300 km no services",    "level": "medium"},
            {"lat": 45.5,  "lon": -122.7, "label": "Urban congestion",               "level": "low"},
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
        zoom = st.slider("Zoom", 3, 14, s.map_zoom, label_visibility="collapsed", key="map_z")
        st.session_state.map_zoom = zoom

    m = build_expedition_map(
        s.map_center, zoom, sel,
        s.show_fuel, s.show_camps, s.show_borders, s.show_safety,
    )
    st_folium(m, width="100%", height=height, returned_objects=[])
