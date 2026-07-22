from typing import Tuple, Dict, Any
from .data import TREKS

def score_trek(user: Dict[str, Any], trek: Dict[str, Any]) -> Tuple[int, str]:
    score = int(trek.get("ai_base", 70))
    reasons = []

    # Experience vs difficulty
    if user.get("experience") == "beginner" and trek["difficulty"] == "hard":
        score -= 20; reasons.append("reduced: beginner vs hard route (-20)")
    if user.get("experience") == "advanced" and trek["difficulty"] == "easy":
        score -= 10; reasons.append("reduced: easy for advanced (-10)")

    # Budget vs cost
    if user.get("budget") == "low" and int(trek["cost_min"]) > 1500:
        score -= 15; reasons.append("reduced: above low budget (-15)")

    # Fitness (light touch)
    if user.get("fitness") == "low" and trek["difficulty"] != "easy":
        score -= 8; reasons.append("reduced: low fitness vs non-easy (-8)")
    if user.get("fitness") == "high" and trek["difficulty"] == "easy":
        score -= 5; reasons.append("reduced: easy vs high fitness (-5)")

    # Clamp
    score = max(0, min(100, score))
    if not reasons:
        reasons.append("good match based on profile")
    return score, "; ".join(reasons)

def get_recommendations(user: Dict[str, Any]):
    recs = []
    for trek in TREKS:
        s, why = score_trek(user, trek)
        recs.append({
            "trek": { **trek, "aiScore": s },
            "reason": why
        })
    recs.sort(key=lambda r: r["trek"]["aiScore"], reverse=True)
    return recs
