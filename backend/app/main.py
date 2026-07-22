import json
from . import places_db
from .osm import fetch_osm


from datetime import date as _date
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    AssessIn, AssessOut, RiskBreakdown, HistoryItem,
    TrekOut, UserProfile, RecoResponse, ChatIn, ChatOut
)
from . import db
from .risk import assess_stub
from .data import TREKS, GUIDES, LODGING
from .reco import get_recommendations
from .chat_logic import respond

from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="Smart Trek Planner API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    db.init_db()
    places_db.init_db()

@app.get("/")
def root():
    return {"ok": True, "service": "smart-trek-planner"}

# ----- TREKS -----
@app.get("/treks", response_model=list[TrekOut])
def list_treks():
    # no scores here; just the catalog; frontend can show aiScore later
    return [TrekOut(**t) for t in TREKS]

@app.get("/treks/{trek_id}", response_model=TrekOut)
def get_trek(trek_id: int):
    for t in TREKS:
        if t["id"] == trek_id:
            return TrekOut(**t)
    raise HTTPException(404, "trek not found")

# ----- RECOMMENDATIONS -----
@app.post("/recommendations", response_model=RecoResponse)
def recommendations(profile: UserProfile):
    recs = get_recommendations(profile.model_dump())
    return {"recommendations": recs}

# ----- DASHBOARD BUNDLE (trek details + guides + lodging) -----
@app.get("/treks/{trek_id}/plan")
def plan_bundle(trek_id: int):
    trek = next((t for t in TREKS if t["id"] == trek_id), None)
    if not trek:
        raise HTTPException(404, "trek not found")
    loc = trek["location"]
    return {
        "trek": trek,
        "guides": GUIDES.get(loc, []),
        "lodging": LODGING.get(loc, []),
        "safety_recs": [
            "Altitude acclimatization required" if trek["altitude"] >= 3000 else "Standard acclimatization",
            "Weather monitoring essential",
            "Emergency evacuation insurance recommended"
        ]
    }

# ----- CHATBOT -----
@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    reply, show_plan, trek_id = respond(payload.message, len(payload.history))
    return ChatOut(reply=reply, showPlan=show_plan, selectedTrekId=trek_id)

# ----- SAFETY / RISK (coords) -----
@app.post("/risk/assess", response_model=AssessOut)
def assess(payload: AssessIn):
    risk = assess_stub(
        payload.lat, payload.lon, payload.date,
        payload.elevation_m, payload.features or {}
    )
    rec = {
        "lat": float(payload.lat),
        "lon": float(payload.lon),
        "date": payload.date or _date.today().isoformat(),
        "elevation_m": float(payload.elevation_m) if payload.elevation_m is not None else None,
        "risk": risk,
        "features_json": None,
    }
    new_id = db.insert_assessment(rec)
    return AssessOut(
        id=int(new_id),
        lat=rec["lat"],
        lon=rec["lon"],
        date=rec["date"],
        elevation_m=rec["elevation_m"],
        risk=RiskBreakdown(**risk),
    )

@app.get("/risk/assess", response_model=AssessOut)
def assess_q(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    date: str | None = None,
    elevation_m: float | None = None,
):
    payload = AssessIn(lat=lat, lon=lon, date=date, elevation_m=elevation_m)
    return assess(payload)

@app.get("/risk/history", response_model=list[HistoryItem])
def history(limit: int = 20):
    rows = db.list_history(limit=limit)
    return [HistoryItem(**r) for r in rows]

@app.get("/risk/{assess_id}", response_model=AssessOut)
def get_assessment(assess_id: int):
    row = db.get_assessment(assess_id)
    if not row:
        raise HTTPException(status_code=404, detail="not found")
    risk = {
        "avalanche_pct": float(row["avalanche_pct"]),
        "blizzard_pct": float(row["blizzard_pct"]),
        "landslide_pct": float(row["landslide_pct"]),
        "overall_pct": float(row["overall_pct"]),
        "label": str(row["label"]),
        "reason": str(row["reason"]),
        "source": str(row["source"]),
    }
    return {
        "id": int(row["id"]),
        "lat": float(row["lat"]),
        "lon": float(row["lon"]),
        "date": str(row["date"]),
        "elevation_m": float(row["elevation_m"]) if row["elevation_m"] is not None else None,
        "risk": risk,
    }

class OSMIngestIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    radius_m: int = Field(2000, ge=100, le=10000)
    kinds: List[str] = Field(default_factory=lambda: ["restaurant","cafe","lodging","resort"])

class IngestReport(BaseModel):
    fetched: int
    inserted_or_updated: int

@app.post("/ingest/osm", response_model=IngestReport)
def ingest_osm(payload: OSMIngestIn):
    items = fetch_osm(payload.lat, payload.lon, payload.radius_m, payload.kinds)
    done = places_db.upsert_many(items)
    return {"fetched": len(items), "inserted_or_updated": done}

# --------- PLACES: nearby search ----------
class PlaceOut(BaseModel):
    id: int
    name: str
    kind: str
    lat: float
    lon: float
    address: str | None = None
    phone: str | None = None
    website: str | None = None
    distance_m: float | None = None
    rating: float | None = None
    price: str | None = None
    tags: dict | None = None

@app.get("/places/nearby", response_model=List[PlaceOut])
def places_nearby(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    radius_m: int = Query(2000, ge=100, le=10000),
    kind: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    out = places_db.search_nearby(lat, lon, radius_m, kind, limit)
    return [
        PlaceOut(
            id=r["id"], name=r["name"], kind=r["kind"], lat=r["lat"], lon=r["lon"],
            address=r.get("address"), phone=r.get("phone"), website=r.get("website"),
            distance_m=r.get("distance_m"), rating=r.get("rating"), price=r.get("price"),
            tags=json.loads(r.get("tags") or "{}")
        ) for r in out
    ]

# --------- PLACES: text search (for RAG) ----------
class PlaceSearchOut(BaseModel):
    id: int
    name: str
    kind: str
    address: str | None = None

@app.get("/places/search", response_model=List[PlaceSearchOut])
def places_search(q: str, limit: int = 20):
    rows = places_db.search_text(q, limit)
    return [{"id": r["id"], "name": r["name"], "kind": r["kind"], "address": r.get("address")} for r in rows]
