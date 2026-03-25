from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime


RecommendationType = Literal[
    "adherence_reminder",
    "activity_prompt",
    "meal_consistency_prompt",
    "glucose_monitoring_reminder",
    "sleep_lifestyle_nudge",
    "clinician_followup_suggestion",
]


class FeatureInput(BaseModel):
    avg_glucose_24h: float = Field(..., ge=0)
    glucose_variability_24h: float = Field(..., ge=0)
    high_glucose_event_count_24h: int = Field(..., ge=0)
    low_glucose_event_count_24h: int = Field(..., ge=0)
    time_in_range_proxy_24h: float = Field(..., ge=0, le=1)
    glucose_trend_3d: float
    glucose_trend_7d: float
    steps_today: int = Field(..., ge=0)
    steps_vs_baseline: float
    sleep_hours_last_night: float = Field(..., ge=0, le=24)
    sleep_vs_baseline: float
    missed_log_count: int = Field(..., ge=0)
    recommendation_ack_rate: float = Field(..., ge=0, le=1)
    last_recommendation_type: str | None = None
    days_since_last_acknowledged_action: int = Field(..., ge=0)


class Recommendation(BaseModel):
    recommendation_id: str
    type: RecommendationType
    priority: int = Field(..., ge=1, le=5)
    message: str
    explanation: str
    confidence: float = Field(..., ge=0, le=1)
    triggered_features: List[str]
    timestamp: datetime
    safe_for_display: bool = True
    requires_clinician_followup: bool = False