import sqlite3, json, math
from typing import Any, Dict, List, Optional
from rapidfuzz import fuzz

DB_PATH = "safety.db"  # reuse your existing DB file

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = _conn(); cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS places(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,        -- 'osm' | 'scrape'
        source_id TEXT NOT NULL,     -- unique id in the source
        name TEXT NOT NULL,
        kind TEXT NOT NULL,          -- 'restaurant' | 'lodging' | 'resort' | 'cafe' ...
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        address TEXT,
        phone TEXT,
        website TEXT,
        rating REAL,
        price TEXT,
        tags TEXT,                   -- JSON string of extra tags
        updated_at TEXT NOT NULL,
        UNIQUE(source, source_id)
    );
    """)
    # simple full-text search table (manual sync)
    cur.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS places_fts USING fts5(
        name, address, tags, content=''
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_places_kind ON places(kind);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_places_latlon ON places(lat,lon);")
    con.commit(); con.close()

def _haversine(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(a))

def upsert_place(p: Dict[str, Any]) -> int:
    """
    p keys: source, source_id, name, kind, lat, lon, address, phone, website, rating, price, tags(dict)
    """
    con = _conn(); cur = con.cursor()
    # try strict upsert on (source, source_id)
    cur.execute("SELECT id FROM places WHERE source=? AND source_id=?;", (p["source"], p["source_id"]))
    row = cur.fetchone()
    tags_json = json.dumps(p.get("tags") or {}, ensure_ascii=False)
    if row:
        cur.execute("""
            UPDATE places SET name=?, kind=?, lat=?, lon=?, address=?, phone=?, website=?, rating=?,
                              price=?, tags=?, updated_at=datetime('now') WHERE id=?;
        """, (p["name"], p["kind"], p["lat"], p["lon"], p.get("address"), p.get("phone"),
              p.get("website"), p.get("rating"), p.get("price"), tags_json, row["id"]))
        pid = row["id"]
    else:
        # near-duplicate check (same kind, ~200m, similar name)
        cur.execute("SELECT id,name,lat,lon FROM places WHERE kind=?;", (p["kind"],))
        dup_id = None
        for r in cur.fetchall():
            if _haversine(p["lat"], p["lon"], r["lat"], r["lon"]) <= 200:
                if fuzz.ratio((p["name"] or "").lower(), (r["name"] or "").lower()) >= 90:
                    dup_id = r["id"]; break
        if dup_id:
            pid = dup_id
            cur.execute("""
                UPDATE places SET name=?, address=COALESCE(address, ?), phone=COALESCE(phone, ?),
                                  website=COALESCE(website, ?), updated_at=datetime('now')
                WHERE id=?;
            """, (p["name"], p.get("address"), p.get("phone"), p.get("website"), pid))
        else:
            cur.execute("""
                INSERT INTO places(source,source_id,name,kind,lat,lon,address,phone,website,rating,price,tags,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'));
            """, (p["source"], p["source_id"], p["name"], p["kind"], p["lat"], p["lon"],
                  p.get("address"), p.get("phone"), p.get("website"), p.get("rating"),
                  p.get("price"), tags_json))
            pid = cur.lastrowid
    # update FTS
    content = " ".join(filter(None, [
        p.get("name"), p.get("address"),
        " ".join([f"{k}:{v}" for k,v in (p.get("tags") or {}).items()])
    ]))
    cur.execute("INSERT INTO places_fts(rowid,name,address,tags) VALUES(?,?,?,?) ON CONFLICT DO NOTHING;", (pid, p.get("name"), p.get("address"), content))
    # If exists, refresh:
    cur.execute("UPDATE places_fts SET name=?, address=?, tags=? WHERE rowid=?;", (p.get("name"), p.get("address"), content, pid))
    con.commit(); con.close()
    return int(pid)

def upsert_many(items: List[Dict[str, Any]]) -> int:
    n = 0
    for it in items:
        try:
            upsert_place(it); n += 1
        except Exception:
            continue
    return n

def search_nearby(lat: float, lon: float, radius_m: int = 2000, kind: Optional[str] = None, limit: int = 50) -> List[dict]:
    con = _conn()
    rows = con.execute("SELECT * FROM places WHERE kind=?;" if kind else "SELECT * FROM places;", (kind,) if kind else ()).fetchall()
    out = []
    for r in rows:
        d = _haversine(lat, lon, r["lat"], r["lon"])
        if d <= radius_m:
            o = dict(r); o["distance_m"] = round(d, 1); out.append(o)
    out.sort(key=lambda x: x["distance_m"])
    return out[:limit]

def search_text(q: str, limit: int = 20) -> List[dict]:
    con = _conn()
    # FTS match; fallback to LIKE if needed
    try:
        ids = con.execute("SELECT rowid FROM places_fts WHERE places_fts MATCH ? LIMIT ?;", (q, limit)).fetchall()
        id_list = [r[0] for r in ids]
        if not id_list: return []
        rows = con.execute(f"SELECT * FROM places WHERE id IN ({','.join(['?']*len(id_list))});", id_list).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        rows = con.execute("SELECT * FROM places WHERE name LIKE ? OR address LIKE ? LIMIT ?;", (f"%{q}%", f"%{q}%", limit)).fetchall()
        return [dict(r) for r in rows]
