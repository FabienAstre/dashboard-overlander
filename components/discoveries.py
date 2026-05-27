import requests
import streamlit as st
import xml.etree.ElementTree as ET
import re

TYPE_META = {
    "viewpoint":           {"icon": "👁",  "label": "Scenic Viewpoint",   "color": "#00d4ff"},
    "attraction":          {"icon": "🏛",  "label": "Tourist Attraction", "color": "#f59e0b"},
    "museum":              {"icon": "🏛",  "label": "Museum",             "color": "#7c3aed"},
    "artwork":             {"icon": "🎨",  "label": "Public Art",         "color": "#ec4899"},
    "ruins":               {"icon": "🗿",  "label": "Ruins",              "color": "#92400e"},
    "archaeological_site": {"icon": "🗿",  "label": "Archaeological",     "color": "#92400e"},
    "monument":            {"icon": "🏛",  "label": "Monument",           "color": "#6b7280"},
    "peak":                {"icon": "🏔",  "label": "Summit",             "color": "#10b981"},
    "beach":               {"icon": "🏖",  "label": "Beach",              "color": "#06b6d4"},
    "hot_spring":          {"icon": "♨️",  "label": "Hot Spring",         "color": "#ef4444"},
    "waterfall":           {"icon": "💧",  "label": "Waterfall",          "color": "#3b82f6"},
    "nature_reserve":      {"icon": "🌿",  "label": "Nature Reserve",     "color": "#10b981"},
}

# Geoapify free tier — 3000 calls/day, no CC required
# Sign up at https://www.geoapify.com — takes 2 minutes
GEOAPIFY_CATEGORIES = [
    "tourism.attraction",
    "tourism.sights.viewpoint",
    "tourism.sights.place_of_worship",
    "natural.beach",
    "natural.water.hot_spring",
    "natural.water.waterfall",
    "natural.mountain",
    "heritage.unesco",
    "heritage.ruins",
]

GEOAPIFY_TYPE_MAP = {
    "tourism.attraction":              ("attraction", "🏛"),
    "tourism.sights.viewpoint":        ("viewpoint",  "👁"),
    "natural.beach":                   ("beach",      "🏖"),
    "natural.water.hot_spring":        ("hot_spring", "♨️"),
    "natural.water.waterfall":         ("waterfall",  "💧"),
    "natural.mountain":                ("peak",       "🏔"),
    "heritage.unesco":                 ("ruins",      "🗿"),
    "heritage.ruins":                  ("ruins",      "🗿"),
}


def _get_geoapify_key():
    try:
        return st.secrets["GEOAPIFY_API_KEY"]
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_discoveries_by_radius(lat, lon, radius_km=150):
    api_key = _get_geoapify_key()
    if not api_key:
        st.warning("Add GEOAPIFY_API_KEY to Streamlit secrets. Free at geoapify.com")
        return []

    places = []
    for category in GEOAPIFY_CATEGORIES:
        try:
            r = requests.get(
                "https://api.geoapify.com/v2/places",
                params={
                    "categories": category,
                    "filter":     "circle:" + str(lon) + "," + str(lat) + "," + str(radius_km * 1000),
                    "limit":      100,
                    "apiKey":     api_key,
                },
                timeout=10,
            )
            r.raise_for_status()
            for feat in r.json().get("features", []):
                props = feat.get("properties", {})
                geom  = feat.get("geometry", {})
                coords = geom.get("coordinates", [None, None])
                name  = props.get("name", "")
                if not name:
                    continue
                ptype, icon = GEOAPIFY_TYPE_MAP.get(category, ("attraction", "🏛"))
                meta = TYPE_META.get(ptype, TYPE_META["attraction"])
                places.append({
                    "name":    name,
                    "lat":     coords[1],
                    "lon":     coords[0],
                    "type":    ptype,
                    "icon":    icon,
                    "label":   meta["label"],
                    "color":   meta["color"],
                    "desc":    props.get("description", "")[:300],
                    "website": props.get("website", ""),
                    "ele":     "",
                })
        except Exception as e:
            continue
    return places


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_discoveries_by_country(country_code="MX"):
    # Country bounding boxes
    BBOXES = {
        "MX": (14.5, -117.1, 32.7, -86.7),
        "US": (24.4, -125.0, 49.4, -66.9),
        "CA": (41.7, -141.0, 83.1, -52.6),
    }
    bbox = BBOXES.get(country_code)
    if not bbox:
        return []
    # Use center of bbox + large radius
    center_lat = (bbox[0] + bbox[2]) / 2
    center_lon = (bbox[1] + bbox[3]) / 2
    radius_km  = int(((bbox[2] - bbox[0]) * 111) / 2)
    return fetch_discoveries_by_radius(center_lat, center_lon, min(radius_km, 500))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_atlas_obscura_rss():
    places = []
    feeds = [
        "https://www.atlasobscura.com/places/feed.rss",
        "https://www.atlasobscura.com/articles/feed.rss",
    ]
    for feed_url in feeds:
        try:
            r = requests.get(
                feed_url,
                headers={"User-Agent": "OverlanderOS/1.0"},
                timeout=10,
            )
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:20]:
                title = item.findtext("title", "")
                link  = item.findtext("link", "")
                desc  = item.findtext("description", "")
                if desc:
                    desc = re.sub("<[^>]+>", "", desc)[:300]
                places.append({
                    "title":  title,
                    "link":   link,
                    "desc":   desc,
                    "source": "Atlas Obscura",
                })
        except Exception:
            continue
    return places


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_wikipedia_nearby(lat, lon, radius_km=50):
    try:
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action":   "query",
                "list":     "geosearch",
                "gscoord":  str(lat) + "|" + str(lon),
                "gsradius": str(min(radius_km * 1000, 10000)),
                "gslimit":  20,
                "format":   "json",
            },
            headers={"User-Agent": "OverlanderOS/1.0"},
            timeout=10,
        )
        results = []
        for p in r.json().get("query", {}).get("geosearch", []):
            results.append({
                "name": p["title"],
                "lat":  p["lat"],
                "lon":  p["lon"],
                "dist": p["dist"],
                "url":  "https://en.wikipedia.org/wiki/" + p["title"].replace(" ", "_"),
            })
        return results
    except Exception:
        return []


def filter_discoveries(places, types=None):
    if not types:
        return places
    return [p for p in places if p["type"] in types]
