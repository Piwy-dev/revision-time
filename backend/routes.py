from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.database import Session as DBSession
from backend.database import DailyTarget, get_db
import backend.models as schemas
from datetime import datetime as dt

router = APIRouter(prefix="/api", tags=["api"])


def calculate_duration(start_time: str, end_time: str) -> int:
    """Calculate duration in minutes between two times in HH:MM format"""
    start = dt.strptime(start_time, "%H:%M")
    end = dt.strptime(end_time, "%H:%M")
    delta = end - start
    return int(delta.total_seconds() / 60)


@router.post("/sessions", response_model=schemas.SessionResponse)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    duration = calculate_duration(session_data.start_time, session_data.end_time)
    if duration <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    db_session = DBSession(
        date=session_data.date,
        start_time=session_data.start_time,
        end_time=session_data.end_time,
        duration_minutes=duration,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/sessions", response_model=list[schemas.SessionResponse])
def get_sessions(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    sessions = db.query(DBSession).filter(
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    return sessions


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(db_session)
    db.commit()
    return {"message": "Session deleted"}


@router.get("/stats/daily", response_model=list[schemas.DailyStats])
def get_daily_stats(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get daily study totals with targets"""
    # Get all sessions in range
    sessions = db.query(DBSession).filter(
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    
    # Get all targets
    targets = {t.day_of_week: t.target_minutes for t in db.query(DailyTarget).all()}
    
    # Build daily stats
    daily_totals = {}
    for session in sessions:
        if session.date not in daily_totals:
            daily_totals[session.date] = {"total_minutes": 0, "sessions": []}
        daily_totals[session.date]["total_minutes"] += session.duration_minutes
        daily_totals[session.date]["sessions"].append(session)
    
    # Generate stats for all dates in range with 0 if no sessions
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    stats = []
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        day_of_week = current.weekday()  # 0=Monday, 6=Sunday
        target = targets.get(day_of_week, 240)  # Default 4 hours
        
        total = daily_totals.get(date_str, {}).get("total_minutes", 0)
        stats.append(schemas.DailyStats(
            date=date_str,
            day_of_week=day_of_week,
            total_minutes=total,
            target_minutes=target,
        ))
        current += timedelta(days=1)
    
    return stats


@router.get("/stats/hourly", response_model=list[schemas.HourlyStats])
def get_hourly_stats(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get hourly distribution of study time"""
    sessions = db.query(DBSession).filter(
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    
    hourly_totals = {h: 0 for h in range(24)}
    
    for session in sessions:
        start_hour = int(session.start_time.split(":")[0])
        end_hour = int(session.end_time.split(":")[0])
        
        # Simple distribution: add duration to start hour
        # (More sophisticated: split across multiple hours if needed)
        if start_hour == end_hour:
            hourly_totals[start_hour] += session.duration_minutes
        else:
            # Split time across hours
            start_min = int(session.start_time.split(":")[1])
            end_min = int(session.end_time.split(":")[1])
            
            # Minutes in start hour
            hourly_totals[start_hour] += (60 - start_min)
            
            # Full hours in between
            for h in range(start_hour + 1, end_hour):
                hourly_totals[h] += 60
            
            # Minutes in end hour
            hourly_totals[end_hour] += end_min
    
    return [schemas.HourlyStats(hour=h, total_minutes=m) for h, m in hourly_totals.items()]


@router.get("/target/{day_of_week}", response_model=schemas.DailyTargetResponse)
def get_target(day_of_week: int, db: Session = Depends(get_db)):
    target = db.query(DailyTarget).filter(DailyTarget.day_of_week == day_of_week).first()
    if not target:
        # Create default if not exists
        target = DailyTarget(day_of_week=day_of_week, target_minutes=240)
        db.add(target)
        db.commit()
        db.refresh(target)
    return target


@router.get("/targets", response_model=list[schemas.DailyTargetResponse])
def get_all_targets(db: Session = Depends(get_db)):
    targets = db.query(DailyTarget).all()
    # Ensure all days exist
    existing_days = {t.day_of_week for t in targets}
    for day in range(7):
        if day not in existing_days:
            target = DailyTarget(day_of_week=day, target_minutes=240)
            db.add(target)
    db.commit()
    targets = db.query(DailyTarget).all()
    return targets


@router.put("/target/{day_of_week}", response_model=schemas.DailyTargetResponse)
def update_target(
    day_of_week: int,
    target_data: schemas.DailyTargetUpdate,
    db: Session = Depends(get_db)
):
    target = db.query(DailyTarget).filter(DailyTarget.day_of_week == day_of_week).first()
    if not target:
        target = DailyTarget(day_of_week=day_of_week, target_minutes=target_data.target_minutes)
        db.add(target)
    else:
        target.target_minutes = target_data.target_minutes
    db.commit()
    db.refresh(target)
    return target
