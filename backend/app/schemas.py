from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Metric(BaseModel):
    name: str
    value: float
    units: str
    confidence: float = Field(ge=0.0, le=1.0)
    notes: Optional[str] = None


class RuleFix(BaseModel):
    issue: str
    evidence: str
    cue: str
    drill: str


class AnalyzeResponse(BaseModel):
    ok: bool
    video_filename: str
    analysis_mode: str
    source: str
    limitations: List[str]
    metrics: List[Metric]
    fixes: List[RuleFix]
    notes: List[str]
    debug: Dict[str, Any] = {}


class UserPreferences(BaseModel):
    shot_style: Optional[str] = None
    do_not_change: List[str] = []
    focus_areas: List[str] = []
    physical_constraints: List[str] = []
    environment_notes: List[str] = []


class ChatRequest(BaseModel):
    message: str
    last_analysis: Optional[Dict[str, Any]] = None
    preferences: Optional[UserPreferences] = None


class ChatResponse(BaseModel):
    ok: bool
    reply: str
