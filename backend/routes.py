from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.database import Session as DBSession
from backend.database import DailyTarget, ExamSession, ExamDailyTarget, get_db
import backend.models as schemas
from datetime import datetime as dt

router = APIRouter(prefix="/api", tags=["api"])


def calculate_duration(start_time: str, end_time: str) -> int:
    """Calculate duration in minutes between two times in HH:MM format"""
    start = dt.strptime(start_time, "%H:%M")
    end = dt.strptime(end_time, "%H:%M")
    delta = end - start
    return int(delta.total_seconds() / 60)


# ==================== EXAM SESSION ENDPOINTS ====================

@router.post("/exam-sessions", response_model=schemas.ExamSessionResponse)
def create_exam_session(session_data: schemas.ExamSessionCreate, db: Session = Depends(get_db)):
    """Create a new exam session"""
    db_session = ExamSession(
        name=session_data.name,
        description=session_data.description,
        start_date=session_data.start_date,
        end_date=session_data.end_date,
        is_active=True,
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/exam-sessions", response_model=list[schemas.ExamSessionResponse])
def list_exam_sessions(db: Session = Depends(get_db)):
    """List all exam sessions"""
    sessions = db.query(ExamSession).order_by(ExamSession.created_at.desc()).all()
    return sessions


@router.get("/exam-sessions/{exam_session_id}", response_model=schemas.ExamSessionResponse)
def get_exam_session(exam_session_id: int, db: Session = Depends(get_db)):
    """Get a specific exam session"""
    session = db.query(ExamSession).filter(ExamSession.id == exam_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    return session


@router.put("/exam-sessions/{exam_session_id}", response_model=schemas.ExamSessionResponse)
def update_exam_session(
    exam_session_id: int,
    session_data: schemas.ExamSessionCreate,
    db: Session = Depends(get_db)
):
    """Update an exam session"""
    session = db.query(ExamSession).filter(ExamSession.id == exam_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    session.name = session_data.name
    session.description = session_data.description
    session.start_date = session_data.start_date
    session.end_date = session_data.end_date
    
    db.commit()
    db.refresh(session)
    return session


@router.delete("/exam-sessions/{exam_session_id}")
def delete_exam_session(exam_session_id: int, db: Session = Depends(get_db)):
    """Delete an exam session and all associated data"""
    session = db.query(ExamSession).filter(ExamSession.id == exam_session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    db.delete(session)
    db.commit()
    return {"message": "Exam session deleted"}


# ==================== SESSION ENDPOINTS (per exam) ====================

@router.post("/sessions", response_model=schemas.SessionResponse)
def create_session(session_data: schemas.SessionCreate, db: Session = Depends(get_db)):
    """Create a study session for an exam"""
    exam_session = db.query(ExamSession).filter(ExamSession.id == session_data.exam_session_id).first()
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    duration = calculate_duration(session_data.start_time, session_data.end_time)
    if duration <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    db_session = DBSession(
        exam_session_id=session_data.exam_session_id,
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
    exam_session_id: int = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get sessions for a specific exam session"""
    sessions = db.query(DBSession).filter(
        DBSession.exam_session_id == exam_session_id,
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    return sessions


@router.put("/sessions/{session_id}", response_model=schemas.SessionResponse)
def update_session(
    session_id: int,
    session_data: schemas.SessionCreate,
    db: Session = Depends(get_db)
):
    """Update a study session"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Verify exam session exists
    exam_session = db.query(ExamSession).filter(ExamSession.id == session_data.exam_session_id).first()
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    # Calculate new duration
    duration = calculate_duration(session_data.start_time, session_data.end_time)
    if duration <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Update session
    db_session.exam_session_id = session_data.exam_session_id
    db_session.date = session_data.date
    db_session.start_time = session_data.start_time
    db_session.end_time = session_data.end_time
    db_session.duration_minutes = duration
    
    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    """Delete a study session"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(db_session)
    db.commit()
    return {"message": "Session deleted"}


# ==================== STATISTICS ENDPOINTS ====================

@router.get("/stats/daily", response_model=list[schemas.DailyStats])
def get_daily_stats(
    exam_session_id: int = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get daily study totals with targets for an exam"""
    exam_session = db.query(ExamSession).filter(ExamSession.id == exam_session_id).first()
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    # Get all sessions in range
    sessions = db.query(DBSession).filter(
        DBSession.exam_session_id == exam_session_id,
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    
    # Get targets for this exam session
    targets = {
        t.day_of_week: t.target_minutes 
        for t in db.query(ExamDailyTarget).filter(
            ExamDailyTarget.exam_session_id == exam_session_id
        ).all()
    }
    
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
    exam_session_id: int = Query(...),
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Session = Depends(get_db)
):
    """Get hourly distribution of study time for an exam"""
    exam_session = db.query(ExamSession).filter(ExamSession.id == exam_session_id).first()
    if not exam_session:
        raise HTTPException(status_code=404, detail="Exam session not found")
    
    sessions = db.query(DBSession).filter(
        DBSession.exam_session_id == exam_session_id,
        DBSession.date >= start_date,
        DBSession.date <= end_date,
    ).all()
    
    hourly_totals = {h: 0 for h in range(24)}
    
    for session in sessions:
        start_hour = int(session.start_time.split(":")[0])
        end_hour = int(session.end_time.split(":")[0])
        
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


# ==================== DAILY TARGET ENDPOINTS ====================

@router.get("/exam-targets/{exam_session_id}", response_model=list[schemas.ExamDailyTargetResponse])
def get_exam_targets(exam_session_id: int, db: Session = Depends(get_db)):
    """Get all daily targets for an exam session"""
    targets = db.query(ExamDailyTarget).filter(
        ExamDailyTarget.exam_session_id == exam_session_id
    ).all()
    
    # Ensure all days exist
    existing_days = {t.day_of_week for t in targets}
    for day in range(7):
        if day not in existing_days:
            target = ExamDailyTarget(exam_session_id=exam_session_id, day_of_week=day, target_minutes=240)
            db.add(target)
    db.commit()
    
    targets = db.query(ExamDailyTarget).filter(
        ExamDailyTarget.exam_session_id == exam_session_id
    ).all()
    return targets


@router.put("/exam-targets/{exam_session_id}/{day_of_week}", response_model=schemas.ExamDailyTargetResponse)
def update_exam_target(
    exam_session_id: int,
    day_of_week: int,
    target_data: schemas.ExamDailyTargetUpdate,
    db: Session = Depends(get_db)
):
    """Update daily target for an exam session"""
    target = db.query(ExamDailyTarget).filter(
        ExamDailyTarget.exam_session_id == exam_session_id,
        ExamDailyTarget.day_of_week == day_of_week
    ).first()
    
    if not target:
        target = ExamDailyTarget(
            exam_session_id=exam_session_id,
            day_of_week=day_of_week,
            target_minutes=target_data.target_minutes
        )
        db.add(target)
    else:
        target.target_minutes = target_data.target_minutes
    
    db.commit()
    db.refresh(target)
    return target


# ==================== LEGACY GLOBAL ENDPOINTS (Optional) ====================

@router.get("/target/{day_of_week}", response_model=schemas.DailyTargetResponse)
def get_target(day_of_week: int, db: Session = Depends(get_db)):
    """Get global daily target (legacy)"""
    target = db.query(DailyTarget).filter(DailyTarget.day_of_week == day_of_week).first()
    if not target:
        target = DailyTarget(day_of_week=day_of_week, target_minutes=240)
        db.add(target)
        db.commit()
        db.refresh(target)
    return target


@router.get("/targets", response_model=list[schemas.DailyTargetResponse])
def get_all_targets(db: Session = Depends(get_db)):
    """Get all global daily targets (legacy)"""
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
    """Update global daily target (legacy)"""
    target = db.query(DailyTarget).filter(DailyTarget.day_of_week == day_of_week).first()
    if not target:
        target = DailyTarget(day_of_week=day_of_week, target_minutes=target_data.target_minutes)
        db.add(target)
    else:
        target.target_minutes = target_data.target_minutes
    db.commit()
    db.refresh(target)
    return target
