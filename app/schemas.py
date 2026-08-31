from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    player_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    player_name: str
    created_at: datetime


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PerformanceCreate(BaseModel):
    match_date: date
    opponent: str = Field(min_length=1, max_length=120)
    position: str = Field(min_length=1, max_length=20)

    minutes_played: int = Field(ge=0, le=130)
    goals: int = Field(default=0, ge=0)
    assists: int = Field(default=0, ge=0)
    shots: int = Field(default=0, ge=0)
    key_passes: int = Field(default=0, ge=0)
    tackles: int = Field(default=0, ge=0)
    interceptions: int = Field(default=0, ge=0)

    rating: float = Field(ge=0, le=10)
    rpe: int = Field(ge=1, le=10)
    notes: str | None = Field(default=None, max_length=2000)


class PerformanceOut(PerformanceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    player_name: str
    created_at: datetime


class MetricSet(BaseModel):
    matches: int
    minutes: int
    goals: int
    assists: int
    goal_contributions: int
    shots: int
    key_passes: int
    tackles: int
    interceptions: int
    average_rating: float
    average_rpe: float
    goals_per_90: float
    assists_per_90: float
    goal_contributions_per_90: float
    shots_per_90: float
    key_passes_per_90: float
    tackles_per_90: float
    interceptions_per_90: float


class TrendValue(BaseModel):
    current: float
    previous: float
    change: float
    direction: Literal["up", "down", "flat"]


class TrendSet(BaseModel):
    average_rating: TrendValue
    goal_contributions_per_90: TrendValue
    key_passes_per_90: TrendValue
    tackles_per_90: TrendValue


class AnalyticsSummary(BaseModel):
    window_size: int
    current: MetricSet
    previous: MetricSet | None
    trends: TrendSet | None
    evidence_note: str
