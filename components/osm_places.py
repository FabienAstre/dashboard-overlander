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


def _run_overpass(query):
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=65,
        )
        r.raise_for_status()
        return _parse_elements(r.json().get("elements", []))
    except Exception as e:
        st.warning("OSM fetch error: " + str(e))
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_by_country(country_code="MX"):
    query = """
[out:json][timeout:55];
area["ISO3166-1"="{cc}"]->.searchArea;
(
  node["tourism"="camp_site"](area.searchArea);
  node["tourism"="caravan_site"](area.searchArea);
  node["amenity"="fuel"](area.searchArea);
  node["amenity"="water_point"](area.searchArea);
  node["amenity"="shower"](area.searchArea);
  way["tourism"="camp_site"](area.searchArea);
  way["amenity"="fuel"](area.searchArea);
);
out center 1000;
""".format(cc=country_code)
    return _run_overpass(query)


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_by_radius(lat, lon, radius_km=200):
    radius_m = radius_km * 1000
    query = """
[out:json][timeout:55];
(
  node["tourism"="camp_site"](around:{r},{lat},{lon});
  node["tourism"="caravan_site"](around:{r},{lat},{lon});
  node["amenity"="fuel"](around:{r},{lat},{lon});
  node["amenity"="water_point"](around:{r},{lat},{lon});
  node["amenity"="shower"](around:{r},{lat},{lon});
  way["tourism"="camp_site"](around:{r},{lat},{lon});
  way["amenity"="fuel"](around:{r},{lat},{lon});
);
out center 1000;
""".format(r=radius_m, lat=lat, lon=lon)
    return _run_overpass(query)


@st.cache_data(ttl=3600, show_spinner=False)
def geocode_place(place):
    # Try Geoapify first
    try:
        api_key = st.secrets.get("GEOAPIFY_API_KEY", "")
        if api_key:
            r = requests.get(
                "https://api.geoapify.com/v1/geocode/search",
                params={
                    "text":   place,
                    "limit":  1,
                    "apiKey": api_key,
                },
                timeout=8,
            )
            r.raise_for_status()
            features = r.json().get("features", [])
            if features:
                coords = features[0]["geometry"]["coordinates"]
                return float(coords[1]), float(coords[0])
    except Exception:
        pass

    # Fallback to Nominatim
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "OverlanderOS/1.0"},
            timeout=8,
        )
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass

    return None


def filter_places(places, types=None):
    if not types:
        return places
    return [p for p in places if p["type"] in types]
