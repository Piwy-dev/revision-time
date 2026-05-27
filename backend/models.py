from pydantic import BaseModel
from datetime import datetime


# Exam Session Schemas
class ExamSessionCreate(BaseModel):
    name: str
    description: str = ""
    start_date: str  # YYYY-MM-DD
    end_date: str = None  # YYYY-MM-DD, optional
    target_minutes: int = 240  # Daily goal in minutes


class ExamSessionResponse(BaseModel):
    id: int
    name: str
    description: str
    start_date: str
    end_date: str = None
    target_minutes: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Session Schemas (now linked to exam sessions)
class SessionCreate(BaseModel):
    exam_session_id: int
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM


class SessionResponse(BaseModel):
    id: int
    exam_session_id: int
    date: str
    start_time: str
    end_time: str
    duration_minutes: int
    created_at: datetime

    class Config:
        from_attributes = True


# Target Schemas
class DailyTargetUpdate(BaseModel):
    target_minutes: int


class DailyTargetResponse(BaseModel):
    id: int
    day_of_week: int
    target_minutes: int

    class Config:
        from_attributes = True


# Statistics Schemas
class DailyStats(BaseModel):
    date: str
    day_of_week: int
    total_minutes: int
    target_minutes: int


class HourlyStats(BaseModel):
    hour: int
    total_minutes: int
