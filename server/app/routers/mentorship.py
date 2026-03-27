from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User, UserRole
from app.models.learning import MentorProfile, MentorSession
from app.core.security import get_current_active_user, require_role
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/mentors", tags=["Mentorship"])


class MentorProfileCreate(BaseModel):
    expertise_areas: List[str] = []
    years_experience: int = 0
    company: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None
    max_mentees: int = 3
    availability_slots: List[dict] = []


class SessionBookRequest(BaseModel):
    mentor_id: int
    scheduled_at: datetime
    duration_minutes: int = 60
    objectives: Optional[str] = None
    meeting_url: Optional[str] = None


class SessionFeedback(BaseModel):
    rating: int
    feedback: Optional[str] = None


@router.get("")
def list_mentors(
    expertise: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    q = db.query(MentorProfile).filter(MentorProfile.is_available == True)
    mentors = q.all()
    result = []
    for m in mentors:
        if expertise and expertise.lower() not in [e.lower() for e in (m.expertise_areas or [])]:
            continue
        result.append({
            "id": m.id,
            "user_id": m.user_id,
            "name": m.user.full_name,
            "avatar_url": m.user.avatar_url,
            "expertise_areas": m.expertise_areas,
            "years_experience": m.years_experience,
            "company": m.company,
            "job_title": m.job_title,
            "bio": m.bio,
            "rating": m.rating,
            "total_sessions": m.total_sessions,
            "max_mentees": m.max_mentees,
        })
    return result


@router.post("/register")
def register_as_mentor(
    payload: MentorProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = db.query(MentorProfile).filter(MentorProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(400, "Already registered as mentor")
    profile = MentorProfile(user_id=current_user.id, **payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"message": "Registered as mentor", "id": profile.id}


@router.post("/sessions/book", status_code=201)
def book_session(
    payload: SessionBookRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    mentor = db.query(MentorProfile).filter(MentorProfile.user_id == payload.mentor_id).first()
    if not mentor:
        raise HTTPException(404, "Mentor not found")

    session = MentorSession(
        mentor_id=payload.mentor_id,
        student_id=current_user.id,
        mentor_profile_id=mentor.id,
        scheduled_at=payload.scheduled_at,
        duration_minutes=payload.duration_minutes,
        objectives=payload.objectives,
        meeting_url=payload.meeting_url,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"message": "Session booked", "session_id": session.id, "scheduled_at": session.scheduled_at}


@router.get("/sessions/mine")
def my_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    as_student = db.query(MentorSession).filter(MentorSession.student_id == current_user.id).all()
    as_mentor = db.query(MentorSession).filter(MentorSession.mentor_id == current_user.id).all()
    return {
        "as_student": [_format_session(s, db) for s in as_student],
        "as_mentor": [_format_session(s, db) for s in as_mentor],
    }


@router.post("/sessions/{session_id}/feedback")
def rate_session(
    session_id: int,
    payload: SessionFeedback,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    session = db.query(MentorSession).filter(
        MentorSession.id == session_id, MentorSession.student_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(404, "Session not found")

    session.student_rating = payload.rating
    session.student_feedback = payload.feedback
    session.status = "completed"

    mentor = session.mentor_profile
    if mentor:
        sessions = db.query(MentorSession).filter(
            MentorSession.mentor_profile_id == mentor.id, MentorSession.student_rating.isnot(None)
        ).all()
        if sessions:
            mentor.rating = round(sum(s.student_rating for s in sessions) / len(sessions), 1)
        mentor.total_sessions = (mentor.total_sessions or 0) + 1

    db.commit()
    return {"message": "Feedback submitted"}


def _format_session(s: MentorSession, db: Session) -> dict:
    mentor_user = db.query(User).filter(User.id == s.mentor_id).first()
    student_user = db.query(User).filter(User.id == s.student_id).first()
    return {
        "id": s.id,
        "mentor_name": mentor_user.full_name if mentor_user else None,
        "student_name": student_user.full_name if student_user else None,
        "scheduled_at": s.scheduled_at,
        "duration_minutes": s.duration_minutes,
        "status": s.status,
        "objectives": s.objectives,
        "meeting_url": s.meeting_url,
        "student_rating": s.student_rating,
    }
