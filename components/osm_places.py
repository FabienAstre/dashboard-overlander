import requests
import streamlit as st

COUNTRIES = {
    "Canada":        "CA",
    "United States": "US",
    "Mexico":        "MX",
}

OSM_TAGS = [
    '"tourism"="camp_site"',
    '"tourism"="caravan_site"',
    '"amenity"="fuel"',
    '"amenity"="water_point"',
    '"amenity"="shower"',
]


def _parse_elements(elements):
    places = []
    for el in elements:
        tags    = el.get("tags", {})
        tourism = tags.get("tourism", "")
        amenity = tags.get("amenity", "")
        name    = tags.get("name", "")

        if tourism in ("camp_site", "caravan_site"):
            ptype, icon = "campsite", "🏕"
        elif amenity == "fuel":
            ptype, icon = "fuel", "⛽"
        elif amenity == "water_point":
            ptype, icon = "water", "💧"
        elif amenity == "shower":
            ptype, icon = "shower", "🚿"
        else:
            continue

        lat = el.get("lat") or (el.get("center", {}).get("lat"))
        lon = el.get("lon") or (el.get("center", {}).get("lon"))
        if not lat or not lon:
            continue

        if not name:
            name = ptype.capitalize() + " (" + str(round(float(lat), 3)) + ")"

        places.append({
            "name":    name,
            "lat":     float(lat),
            "lon":     float(lon),
            "type":    ptype,
            "icon":    icon,
            "fee":     tags.get("fee", "unknown"),
            "surface": tags.get("surface", ""),
            "brand":   tags.get("brand", ""),
            "access":  tags.get("access", "yes"),
        })
    return places


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_by_country(country_code="MX"):
    tag_union = "\n".join(
        "  node[" + t + "](area.country);"
        for t in OSM_TAGS
    )
    query = """
    [out:json][timeout:60];
    area["ISO3166-1"="{cc}"]->.country;
    (
    {tags}
    );
    out body;
    """.format(cc=country_code, tags=tag_union)
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=65,
        )
        r.raise_for_status()
        return _parse_elements(r.json().get("elements", []))
    except Exception as e:
        st.warning("OSM country fetch error: " + str(e))
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_by_radius(lat, lon, radius_km=200):
    radius_m  = radius_km * 1000
    tag_union = "\n".join(
        "  node[" + t + "](around:" + str(radius_m) + "," + str(lat) + "," + str(lon) + ");"
        for t in OSM_TAGS
    )
    query = """
    [out:json][timeout:60];
    (
    {tags}
    );
    out body;
    """.format(tags=tag_union)
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=65,
        )
        r.raise_for_status()
        return _parse_elements(r.json().get("elements", []))
    except Exception as e:
        st.warning("OSM radius fetch error: " + str(e))
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_place(place):
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


def filter_places(places, types=None):
    if types:
        return [p for p in places if p["type"] in types]
    return places
