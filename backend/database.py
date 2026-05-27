from sqlalchemy import create_engine, Column, Integer, String, DateTime, Time, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./study.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # e.g., "Math Exam", "Python Course"
    description = Column(String, nullable=True)
    start_date = Column(String)  # YYYY-MM-DD format
    end_date = Column(String, nullable=True)  # YYYY-MM-DD format
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    study_sessions = relationship("Session", back_populates="exam_session", cascade="all, delete-orphan")
    daily_targets = relationship("ExamDailyTarget", back_populates="exam_session", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), index=True)
    date = Column(String, index=True)  # YYYY-MM-DD format
    start_time = Column(String)  # HH:MM format
    end_time = Column(String)  # HH:MM format
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    exam_session = relationship("ExamSession", back_populates="study_sessions")


class DailyTarget(Base):
    __tablename__ = "daily_targets"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    target_minutes = Column(Integer, default=240)  # Default 4 hours


class ExamDailyTarget(Base):
    __tablename__ = "exam_daily_targets"

    id = Column(Integer, primary_key=True, index=True)
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), index=True)
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    target_minutes = Column(Integer, default=240)  # Default 4 hours
    
    # Relationship
    exam_session = relationship("ExamSession", back_populates="daily_targets")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
