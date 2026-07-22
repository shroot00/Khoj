# app/data.py

TREKS = [
    {
        "id": 1,
        "name": "Everest Base Camp",
        "difficulty": "hard",
        "altitude": 5364,
        "duration": 14,
        "location": "Nepal",
        "bestSeason": "Oct-Nov, Mar-May",
        "highlights": ["World's highest peak base", "Sherpa culture", "Stunning mountain views"],
        "gear": ["High-altitude gear", "Warm sleeping bag", "Trekking poles"],
        "cost_min": 2500,
        "cost_max": 4000,
        "riskLevel": "high",
        "ai_base": 85,
    },
    {
        "id": 2,
        "name": "Annapurna Circuit",
        "difficulty": "moderate",
        "altitude": 5416,
        "duration": 12,
        "location": "Nepal",
        "bestSeason": "Oct-Nov, Mar-May",
        "highlights": ["Diverse landscapes", "Cultural villages", "Thorong La Pass"],
        "gear": ["Standard trekking gear", "Layers", "Good boots"],
        "cost_min": 1200,
        "cost_max": 2500,
        "riskLevel": "medium",
        "ai_base": 92,
    },
    {
        "id": 3,
        "name": "Torres del Paine W Trek",
        "difficulty": "moderate",
        "altitude": 1200,
        "duration": 5,
        "location": "Chile",
        "bestSeason": "Dec-Mar",
        "highlights": ["Dramatic granite towers", "Glacial lakes", "Diverse wildlife"],
        "gear": ["Wind-resistant jacket", "Hiking boots", "Rain gear"],
        "cost_min": 800,
        "cost_max": 1500,
        "riskLevel": "low",
        "ai_base": 88,
    },
]

GUIDES = {
    "Nepal": [
        {"name": "Sherpa Adventures", "rating": 4.9, "reviews": 127, "price_per_day": 280},
        {"name": "Mountain Guides Co.", "rating": 4.7, "reviews": 89, "price_per_day": 250},
    ],
    "Chile": [
        {"name": "Patagonia Trek Pro", "rating": 4.8, "reviews": 66, "price_per_day": 220},
    ],
}

LODGING = {
    "Nepal": [
        {"type": "Tea Houses", "price_range": "$10-25/night"},
        {"type": "Lodge Rooms", "price_range": "$25-50/night"},
        {"type": "Private Rooms", "price_range": "$50-100/night"},
    ],
    "Chile": [
        {"type": "Refugios", "price_range": "$30-60/night"},
        {"type": "Campsites", "price_range": "$10-25/night"},
    ],
}
