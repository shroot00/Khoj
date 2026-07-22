import sqlite3
from typing import Any, Dict

DB_PATH = "safety.db"

def _conn():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = _conn(); cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS assessments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        date TEXT NOT NULL,
        elevation_m REAL,
        avalanche_pct REAL NOT NULL,
        blizzard_pct REAL NOT NULL,
        landslide_pct REAL NOT NULL,
        overall_pct REAL NOT NULL,
        label TEXT NOT NULL,
        reason TEXT NOT NULL,
        source TEXT NOT NULL,
        features_json TEXT,
        created_at TEXT NOT NULL
    );
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_assess_date ON assessments(date);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_assess_coords ON assessments(lat, lon);")
    con.commit(); con.close()

def insert_assessment(rec: Dict[str, Any]) -> int:
    con = _conn(); cur = con.cursor()
    cur.execute("""
    INSERT INTO assessments
    (lat,lon,date,elevation_m,avalanche_pct,blizzard_pct,landslide_pct,overall_pct,label,reason,source,features_json,created_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'));
    """, (
        rec["lat"], rec["lon"], rec["date"], rec.get("elevation_m"),
        rec["risk"]["avalanche_pct"], rec["risk"]["blizzard_pct"], rec["risk"]["landslide_pct"],
        rec["risk"]["overall_pct"], rec["risk"]["label"], rec["risk"]["reason"], rec["risk"]["source"],
        rec.get("features_json"),
    ))
    rid = cur.lastrowid
    con.commit(); con.close()
    return rid

def get_assessment(assess_id: int) -> dict | None:
    con = _conn()
    row = con.execute("SELECT * FROM assessments WHERE id=?", (assess_id,)).fetchone()
    con.close()
    return dict(row) if row else None

def list_history(limit: int = 20) -> list[dict]:
    con = _conn()
    rows = con.execute(
        "SELECT id,lat,lon,date,overall_pct,label,created_at FROM assessments ORDER BY id DESC LIMIT ?;", (limit,)
    ).fetchall()
    con.close()
    return [dict(r) for r in rows]
