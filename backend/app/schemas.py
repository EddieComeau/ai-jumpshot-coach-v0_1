from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class Metric(BaseModel):
    name: str = Field(description="Stable metric identifier owned by the analysis layer.")
    value: float = Field(description="Current measurement value returned by analysis.")
    units: str = Field(description="Display units for the returned metric value.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the returned metric value. Low values should be treated as limited or placeholder confidence.",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Optional metric note, including placeholder or capture limitations when applicable.",
    )


class RuleFix(BaseModel):
    issue: str
    evidence: str
    cue: str
    drill: str


class AnalyzeResponse(BaseModel):
    ok: bool
    video_filename: str
    analysis_mode: str = Field(description="Analysis mode for this run, such as placeholder or future real measurement modes.")
    source: str = Field(description="Source that produced the current analysis payload.")
    limitations: List[str] = Field(
        description="Explicit limitations that bound what is currently known from the uploaded video."
    )
    metrics: List[Metric]
    fixes: List[RuleFix]
    notes: List[str]
    debug: Dict[str, Any] = Field(default_factory=dict)


class UserPreferences(BaseModel):
    shot_style: Optional[str] = None
    do_not_change: List[str] = Field(default_factory=list)
    focus_areas: List[str] = Field(default_factory=list)
    physical_constraints: List[str] = Field(default_factory=list)
    environment_notes: List[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str
    last_analysis: Optional[Dict[str, Any]] = None
    preferences: Optional[UserPreferences] = None


class ChatResponse(BaseModel):
    ok: bool
    reply: str
