from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PerformanceCreate(BaseModel):
    player_name: str = Field(min_length=1, max_length=120)
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
    created_at: datetime
