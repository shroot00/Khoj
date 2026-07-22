from rapidfuzz import fuzz

from .data import TREKS

GREETINGS = ("hi", "hello", "hey", "namaste")


def _find_trek(message: str):
    best, best_score = None, 0
    for t in TREKS:
        score = max(
            fuzz.partial_ratio(message, t["name"].lower()),
            fuzz.partial_ratio(message, t["location"].lower()),
        )
        if score > best_score:
            best, best_score = t, score
    return best if best_score >= 70 else None


def respond(message: str, history_len: int = 0):
    msg = message.strip().lower()

    if not msg:
        return 'Ask me about a trek (e.g. "Everest Base Camp") or say hi!', False, None

    if len(msg) < 20 and any(g in msg for g in GREETINGS):
        return (
            "Hey! I'm your trek planning assistant. Ask me about a trek, "
            "its difficulty, altitude, or best season.",
            False, None,
        )

    trek = _find_trek(msg)
    if trek:
        reply = (
            f"{trek['name']} ({trek['location']}) is a {trek['difficulty']} trek reaching "
            f"{trek['altitude']}m over {trek['duration']} days. Best season: {trek['bestSeason']}. "
            f"Estimated cost: ${trek['cost_min']}-${trek['cost_max']}. Risk level: {trek['riskLevel']}."
        )
        return reply, True, trek["id"]

    if any(k in msg for k in ("risk", "avalanche", "safety", "blizzard", "landslide")):
        return (
            "You can check avalanche/blizzard/landslide risk for specific coordinates "
            "using the Risk Assessment tool.",
            False, None,
        )

    if any(k in msg for k in ("recommend", "suggest", "best trek")):
        return (
            "Tell me your experience level, fitness, and budget in the Recommendations "
            "tab and I'll suggest a trek for you.",
            False, None,
        )

    return (
        "I can help with trek details, recommendations, and safety risk info. "
        'Try asking about a trek by name (e.g. "Annapurna Circuit") or its location (e.g. "Nepal").',
        False, None,
    )
