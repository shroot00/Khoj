import httpx
from typing import List, Dict

OSM_KINDS = {
    "restaurant": [('amenity','restaurant')],
    "cafe": [('amenity','cafe'), ('amenity','fast_food')],
    "lodging": [('tourism','hotel'), ('tourism','guest_house'), ('tourism','hostel'), ('tourism','motel'), ('tourism','alpine_hut')],
    "resort": [('tourism','resort')],
}

def _build_overpass(lat: float, lon: float, radius_m: int, kinds: list[str]) -> str:
    # nodes/ways/relations with a center, around given point
    clauses = []
    for kind in kinds:
        for k,v in OSM_KINDS.get(kind, []):
            for typ in ("node","way","relation"):
                clauses.append(f'{typ}["{k}"="{v}"](around:{radius_m},{lat},{lon});')
    body = "\n".join(clauses)
    return f"[out:json][timeout:25];({body});out center;"

def fetch_osm(lat: float, lon: float, radius_m: int = 2000, kinds: list[str] = ["restaurant","cafe","lodging","resort"]) -> List[Dict]:
    ql = _build_overpass(lat, lon, radius_m, kinds)
    headers = {"User-Agent": "smart-trek-planner/0.1 (hackathon)"}
    with httpx.Client(timeout=30) as client:
        r = client.post("https://overpass-api.de/api/interpreter", data={"data": ql}, headers=headers)
        r.raise_for_status()
        data = r.json()
    out = []
    for el in data.get("elements", []):
        tags = el.get("tags", {}) or {}
        name = tags.get("name")
        if not name: continue
        lat2, lon2 = None, None
        if "lat" in el and "lon" in el:
            lat2, lon2 = el["lat"], el["lon"]
        elif "center" in el:
            lat2, lon2 = el["center"]["lat"], el["center"]["lon"]
        else:
            continue
        knd = None
        for k in kinds:
            for tk, tv in OSM_KINDS.get(k, []):
                if tags.get(tk) == tv:
                    knd = k; break
            if knd: break
        addr = ", ".join(filter(None, [tags.get("addr:street"), tags.get("addr:place"), tags.get("addr:city")]))
        out.append({
            "source": "osm",
            "source_id": f'{el.get("type","node")}:{el.get("id")}',
            "name": name,
            "kind": knd or "poi",
            "lat": float(lat2),
            "lon": float(lon2),
            "address": addr or None,
            "phone": tags.get("phone") or tags.get("contact:phone"),
            "website": tags.get("website") or tags.get("contact:website"),
            "rating": None,
            "price": None,
            "tags": tags,
        })
    return out
