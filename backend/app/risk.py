from datetime import date as _date

def _month(date_str: str | None) -> int:
    if date_str:
        return _date.fromisoformat(date_str).month
    return _date.today().month

def assess_stub(lat: float, lon: float, date_str: str | None = None, elevation_m: float | None = None, features: dict | None = None):
    m = _month(date_str)
    blizzard = 45.0 if m in (12,1,2) else 15.0
    landslide = 40.0 if m in (6,7,8,9) else 12.0
    avalanche = 30.0 if m in (12,1,2,3) else 18.0

    if elevation_m is not None:
        if elevation_m >= 5500: avalanche += 10; blizzard += 10
        elif elevation_m <= 3000: landslide += 5

    avalanche = max(0.0, min(100.0, round(avalanche,1)))
    blizzard  = max(0.0, min(100.0, round(blizzard,1)))
    landslide = max(0.0, min(100.0, round(landslide,1)))

    overall = round(0.45*avalanche + 0.35*blizzard + 0.20*landslide, 1)
    label = ("LOW" if overall < 20 else "MODERATE" if overall < 40 else
             "ELEVATED" if overall < 60 else "HIGH" if overall < 80 else "EXTREME")

    reasons = []
    if m in (12,1,2): reasons.append("winter conditions")
    if m in (6,7,8,9): reasons.append("monsoon period")
    if elevation_m and elevation_m >= 5500: reasons.append("very high elevation")
    if not reasons: reasons.append("seasonal baseline")

    return {
        "avalanche_pct": avalanche,
        "blizzard_pct": blizzard,
        "landslide_pct": landslide,
        "overall_pct": overall,
        "label": label,
        "reason": ", ".join(reasons),
        "source": "stub_v1"
    }
