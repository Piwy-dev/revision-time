from pydantic import BaseModel
from datetime import datetime


class SessionCreate(BaseModel):
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM


class SessionResponse(BaseModel):
    id: int
    date: str
    start_time: str
    end_time: str
    duration_minutes: int
    created_at: datetime

    class Config:
        from_attributes = True


class DailyTargetUpdate(BaseModel):
    target_minutes: int


class DailyTargetResponse(BaseModel):
    id: int
    day_of_week: int
    target_minutes: int

    class Config:
        from_attributes = True


class DailyStats(BaseModel):
    date: str
    day_of_week: int
    total_minutes: int
    target_minutes: int


class HourlyStats(BaseModel):
    hour: int
    total_minutes: int
