from typing import Optional, Any, List, Literal
from pydantic import BaseModel, Field, field_validator

# ----------- Safety / Risk -----------
class AssessIn(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    date: Optional[str] = None
    elevation_m: Optional[float] = Field(None, ge=-500, le=9000)
    features: Optional[dict[str, Any]] = None

    @field_validator("date")
    @classmethod
    def _date_fmt(cls, v):
        if v is None: return v
        from datetime import date as _d
        _d.fromisoformat(v)  # raises if bad
        return v

class RiskBreakdown(BaseModel):
    avalanche_pct: float
    blizzard_pct: float
    landslide_pct: float
    overall_pct: float
    label: str
    reason: str
    source: str

class AssessOut(BaseModel):
    id: int
    lat: float
    lon: float
    date: str
    elevation_m: float | None = None
    risk: RiskBreakdown

class HistoryItem(BaseModel):
    id: int
    lat: float
    lon: float
    date: str
    overall_pct: float
    label: str
    created_at: str

# ----------- Treks / Recs -----------
Difficulty = Literal["easy", "moderate", "hard"]
RiskLevel = Literal["low", "medium", "high"]

class Trek(BaseModel):
    id: int
    name: str
    difficulty: Difficulty
    altitude: int
    duration: int
    location: str
    bestSeason: str
    highlights: list[str]
    gear: list[str]
    cost_min: int
    cost_max: int
    riskLevel: RiskLevel
    ai_base: int  # starting score (0-100)

class TrekOut(Trek):
    aiScore: int | None = None

class UserProfile(BaseModel):
    experience: Literal["beginner", "intermediate", "advanced"] = "beginner"
    fitness: Literal["low", "moderate", "high"] = "moderate"
    budget: Literal["low", "medium", "high"] = "medium"
    preferences: list[str] = []

class TrekReco(BaseModel):
    trek: TrekOut
    reason: str

class RecoResponse(BaseModel):
    recommendations: list[TrekReco]

# ----------- Chatbot -----------
class ChatIn(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)  # [{type:'user'|'ai', text:str}]

class ChatOut(BaseModel):
    reply: str
    showPlan: bool = False
    selectedTrekId: int | None = None
