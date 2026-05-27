import streamlit as st
import folium
from streamlit_folium import st_folium

TILESETS = {
    "CartoDB Dark Matter": {"tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap, © CARTO"},
    "CartoDB Voyager":     {"tiles": "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", "attr": "© OpenStreetMap, © CARTO"},
    "OpenStreetMap":       {"tiles": "OpenStreetMap", "attr": "© OpenStreetMap contributors"},
    "Esri Satellite":      {"tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "attr": "Tiles © Esri"},
}

ROUTE_COORDS = [
    [50.67,-120.33],[49.80,-119.50],[49.03,-119.46],[47.66,-117.43],
    [45.52,-122.68],[40.58,-122.38],[38.58,-121.49],[34.05,-118.24],
    [32.52,-117.04],[31.87,-116.60],[27.97,-114.06],[26.01,-111.34],
    [24.14,-110.31],[22.89,-109.92],
]

def _icon(emoji, size=24):
    return folium.DivIcon(html=f'<div style="font-size:{size}px;">{emoji}</div>',
                          icon_size=(size+4,size+4), icon_anchor=(size//2,size//2))

def build_expedition_map(center, zoom, tileset_name="CartoDB Dark Matter",
                         show_fuel=True, show_camps=True, show_borders=True, show_safety=True):
    ts = TILESETS.get(tileset_name, TILESETS["CartoDB Dark Matter"])
    if ts["tiles"] == "OpenStreetMap":
        m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    else:
        m = folium.Map(location=center, zoom_start=zoom, tiles=ts["tiles"], attr=ts["attr"])

    folium.PolyLine(ROUTE_COORDS, color="#00d4ff", weight=3, opacity=0.85, tooltip="Route").add_to(m)
    folium.PolyLine(ROUTE_COORDS, color="#00d4ff", weight=7, opacity=0.15).add_to(m)
    folium.Marker(ROUTE_COORDS[0],  icon=_icon("🟢"), tooltip="Origin: Kamloops").add_to(m)
    folium.Marker(ROUTE_COORDS[-1], icon=_icon("🏁"), tooltip="Destination: Cabo").add_to(m)

    for wc in ROUTE_COORDS[1:-1]:
        folium.CircleMarker(wc, radius=4, color="#f59e0b", fill=True, fill_color="#f59e0b", fill_opacity=0.8).add_to(m)

    if show_fuel:
        fg = folium.FeatureGroup(name="Fuel Stops")
        for fs in st.session_state.fuel_stops:
            folium.Marker([fs["lat"],fs["lon"]], icon=_icon("⛽",20),
                          tooltip=f"<b>{fs['name']}</b><br>km {fs['dist_km']:,}").add_to(fg)
        fg.add_to(m)

    if show_camps:
        cg = folium.FeatureGroup(name="Campsites")
        for c in st.session_state.campsites:
            folium.Marker([c["lat"],c["lon"]], icon=_icon("🏕",20),
                          tooltip=f"<b>{c['name']}</b><br>{c['type']} · Score {c['score']}").add_to(cg)
        cg.add_to(m)

    if show_borders:
        bg = folium.FeatureGroup(name="Borders")
        for bc in st.session_state.border_crossings:
            folium.Marker([bc["lat"],bc["lon"]], icon=_icon("🛂",22),
                          tooltip=f"<b>{bc['name']}</b><br>{bc['country']}<br>Wait ~{bc['wait_min']} min").add_to(bg)
        bg.add_to(m)

    if show_safety:
        for hz in [
            {"lat":32.6,"lon":-117.1,"label":"High theft risk — TJ border","level":"high"},
            {"lat":27.9,"lon":-114.1,"label":"Remote — 300 km no services","level":"medium"},
            {"lat":45.5,"lon":-122.7,"label":"Urban congestion","level":"low"},
        ]:
            color = {"high":"#ef4444","medium":"#f59e0b","low":"#3b82f6"}[hz["level"]]
            folium.Circle([hz["lat"],hz["lon"]], radius=40000, color=color,
                          fill=True, fill_color=color, fill_opacity=0.08, tooltip=hz["label"]).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m

def render_map(height=520):
    s = st.session_state
    ts_options = list(TILESETS.keys())
    c1, c2 = st.columns([3,1])
    with c1:
        sel = st.selectbox("Style", ts_options,
                           index=ts_options.index(s.get("selected_tileset","CartoDB Dark Matter")),
                           label_visibility="collapsed", key="map_ts")
        st.session_state.selected_tileset = sel
    with c2:
        zoom = st.slider("Zoom", 3, 14, s.map_zoom, label_visibility="collapsed", key="map_z")
        st.session_state.map_zoom = zoom

    m = build_expedition_map(s.map_center, zoom, sel, s.show_fuel, s.show_camps, s.show_borders, s.show_safety)
    st_folium(m, width="100%", height=height, returned_objects=[])
