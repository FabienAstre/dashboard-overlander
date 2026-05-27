import requests
import streamlit as st
import xml.etree.ElementTree as ET

OSM_DISCOVERY_TAGS = [
    '"tourism"="viewpoint"',
    '"tourism"="attraction"',
    '"tourism"="museum"',
    '"tourism"="artwork"',
    '"historic"="ruins"',
    '"historic"="archaeological_site"',
    '"historic"="monument"',
    '"natural"="peak"',
    '"natural"="beach"',
    '"natural"="hot_spring"',
    '"natural"="waterfall"',
    '"leisure"="nature_reserve"',
]

TYPE_META = {
    "viewpoint":            {"icon": "👁",  "label": "Scenic Viewpoint",    "color": "#00d4ff"},
    "attraction":           {"icon": "🏛",  "label": "Tourist Attraction",  "color": "#f59e0b"},
    "museum":               {"icon": "🏛",  "label": "Museum",              "color": "#7c3aed"},
    "artwork":              {"icon": "🎨",  "label": "Public Art",          "color": "#ec4899"},
    "ruins":                {"icon": "🗿",  "label": "Ruins",               "color": "#92400e"},
    "archaeological_site":  {"icon": "🗿",  "label": "Archaeological Site", "color": "#92400e"},
    "monument":             {"icon": "🏛",  "label": "Monument",            "color": "#6b7280"},
    "peak":                 {"icon": "🏔",  "label": "Summit",              "color": "#10b981"},
    "beach":                {"icon": "🏖",  "label": "Beach",               "color": "#06b6d4"},
    "hot_spring":           {"icon": "♨️",  "label": "Hot Spring",          "color": "#ef4444"},
    "waterfall":            {"icon": "💧",  "label": "Waterfall",           "color": "#3b82f6"},
    "nature_reserve":       {"icon": "🌿",  "label": "Nature Reserve",      "color": "#10b981"},
}


def _parse_discovery_elements(elements):
    places = []
    for el in elements:
        tags    = el.get("tags", {})
        tourism = tags.get("tourism", "")
        historic= tags.get("historic", "")
        natural = tags.get("natural", "")
        leisure = tags.get("leisure", "")
        name    = tags.get("name", "")
        desc    = tags.get("description", "") or tags.get("wikipedia", "")

        ptype = tourism or historic or natural or leisure
        if not ptype or ptype not in TYPE_META:
            continue

        lat = el.get("lat") or (el.get("center", {}).get("lat"))
        lon = el.get("lon") or (el.get("center", {}).get("lon"))
        if not lat or not lon:
            continue

        meta = TYPE_META[ptype]
        if not name:
            name = meta["label"] + " (" + str(round(float(lat), 3)) + ")"

        places.append({
            "name":    name,
            "lat":     float(lat),
            "lon":     float(lon),
            "type":    ptype,
            "icon":    meta["icon"],
            "label":   meta["label"],
            "color":   meta["color"],
            "desc":    desc[:300] if desc else "",
            "ele":     tags.get("ele", ""),
            "website": tags.get("website", ""),
        })
    return places


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_discoveries_by_country(country_code="MX"):
    tag_union = "\n".join(
        "  node[" + t + "](area.country);\n"
        "  way["  + t + "](area.country);"
        for t in OSM_DISCOVERY_TAGS
    )
    query = """
    [out:json][timeout:60];
    area["ISO3166-1"="{cc}"]->.country;
    (
    {tags}
    );
    out center body;
    """.format(cc=country_code, tags=tag_union)
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=65,
        )
        r.raise_for_status()
        return _parse_discovery_elements(r.json().get("elements", []))
    except Exception as e:
        st.warning("OSM discoveries fetch error: " + str(e))
        return []


@st.cache_data(ttl=86400, show_spinner=False)
def fetch_discoveries_by_radius(lat, lon, radius_km=150):
    radius_m  = radius_km * 1000
    tag_union = "\n".join(
        "  node[" + t + "](around:" + str(radius_m) + "," + str(lat) + "," + str(lon) + ");\n"
        "  way["  + t + "](around:" + str(radius_m) + "," + str(lat) + "," + str(lon) + ");"
        for t in OSM_DISCOVERY_TAGS
    )
    query = """
    [out:json][timeout:60];
    (
    {tags}
    );
    out center body;
    """.format(tags=tag_union)
    try:
        r = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=65,
        )
        r.raise_for_status()
        return _parse_discovery_elements(r.json().get("elements", []))
    except Exception as e:
        st.warning("OSM radius fetch error: " + str(e))
        return []


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
                    import re
                    desc = re.sub("<[^>]+>", "", desc)[:300]
                places.append({
                    "title": title,
                    "link":  link,
                    "desc":  desc,
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
                "action":    "query",
                "list":      "geosearch",
                "gscoord":   str(lat) + "|" + str(lon),
                "gsradius":  str(min(radius_km * 1000, 10000)),
                "gslimit":   20,
                "format":    "json",
            },
            headers={"User-Agent": "OverlanderOS/1.0"},
            timeout=10,
        )
        data = r.json()
        results = []
        for p in data.get("query", {}).get("geosearch", []):
            results.append({
                "name":  p["title"],
                "lat":   p["lat"],
                "lon":   p["lon"],
                "dist":  p["dist"],
                "url":   "https://en.wikipedia.org/wiki/" + p["title"].replace(" ", "_"),
            })
        return results
    except Exception:
        return []


def filter_discoveries(places, types=None):
    if not types:
        return places
    return [p for p in places if p["type"] in types]
