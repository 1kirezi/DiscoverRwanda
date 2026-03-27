from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.database import get_db
from app.models.user import User, UserRole, VerificationStatus
from app.models.challenge import Challenge, ChallengeStatus, Team
from app.models.project import Project, ImpactMetric
from app.models.learning import LearningProgress, UserBadge, MentorSession
from app.core.security import require_role

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

AdminUser = Depends(require_role(UserRole.ADMIN))


@router.get("/analytics")
def platform_analytics(db: Session = Depends(get_db), _: User = AdminUser):
    total_users = db.query(func.count(User.id)).scalar()
    students = db.query(func.count(User.id)).filter(User.role == UserRole.STUDENT).scalar()
    businesses = db.query(func.count(User.id)).filter(User.role == UserRole.BUSINESS).scalar()
    faculty = db.query(func.count(User.id)).filter(User.role == UserRole.FACULTY).scalar()

    total_challenges = db.query(func.count(Challenge.id)).scalar()
    active_challenges = db.query(func.count(Challenge.id)).filter(Challenge.status == ChallengeStatus.ACTIVE).scalar()
    pending_review = db.query(func.count(Challenge.id)).filter(Challenge.status == ChallengeStatus.SUBMITTED).scalar()

    total_teams = db.query(func.count(Team.id)).scalar()
    total_projects = db.query(func.count(Project.id)).scalar()
    completed_projects = db.query(func.count(Project.id)).filter(Project.status == "completed").scalar()

    total_badges_awarded = db.query(func.count(UserBadge.id)).scalar()
    completed_paths = db.query(func.count(LearningProgress.id)).filter(LearningProgress.is_completed == True).scalar()
    total_sessions = db.query(func.count(MentorSession.id)).filter(MentorSession.status == "completed").scalar()

    pending_verifications = db.query(func.count(User.id)).filter(
        User.verification_status == VerificationStatus.PENDING
    ).scalar()

    return {
        "users": {
            "total": total_users,
            "students": students,
            "businesses": businesses,
            "faculty": faculty,
            "pending_verifications": pending_verifications,
        },
        "challenges": {
            "total": total_challenges,
            "active": active_challenges,
            "pending_review": pending_review,
        },
        "projects": {
            "total": total_teams,
            "active_projects": total_projects,
            "completed": completed_projects,
        },
        "learning": {
            "badges_awarded": total_badges_awarded,
            "completed_paths": completed_paths,
            "mentor_sessions": total_sessions,
        },
    }


@router.get("/users")
def list_users(
    role: Optional[str] = Query(None),
    verification: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: User = AdminUser,
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if verification:
        q = q.filter(User.verification_status == verification)
    if search:
        q = q.filter(
            (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )
    users = q.offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "verification_status": u.verification_status,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.put("/users/{user_id}/toggle-active")
def toggle_user_active(user_id: int, db: Session = Depends(get_db), _: User = AdminUser):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}", "is_active": user.is_active}


@router.get("/verifications")
def pending_verifications(db: Session = Depends(get_db), _: User = AdminUser):
    users = db.query(User).filter(User.verification_status == VerificationStatus.PENDING).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "documents": u.verification_documents,
            "business_name": u.business_profile.business_name if u.business_profile else None,
            "submitted_at": u.updated_at or u.created_at,
        }
        for u in users
    ]


@router.put("/verifications/{user_id}")
def process_verification(
    user_id: int,
    action: str = Query(..., pattern="^(approve|reject)$"),
    db: Session = Depends(get_db),
    _: User = AdminUser,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    user.verification_status = (
        VerificationStatus.APPROVED if action == "approve" else VerificationStatus.REJECTED
    )
    db.commit()
    return {"message": f"Verification {action}d for {user.email}"}


@router.get("/challenges/pending")
def pending_challenges(db: Session = Depends(get_db), _: User = AdminUser):
    challenges = db.query(Challenge).filter(Challenge.status == ChallengeStatus.SUBMITTED).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "business_owner": c.business_owner.full_name if c.business_owner else None,
            "category": c.category,
            "difficulty_level": c.difficulty_level,
            "required_skills": c.required_skills,
            "submitted_at": c.created_at,
        }
        for c in challenges
    ]


@router.get("/impact-metrics")
def all_impact_metrics(db: Session = Depends(get_db), _: User = AdminUser):
    metrics = db.query(ImpactMetric).all()
    return [
        {
            "id": m.id,
            "project_id": m.project_id,
            "metric_type": m.metric_type,
            "value": m.value,
            "description": m.description,
            "verified": m.verified,
            "reported_at": m.reported_at,
        }
        for m in metrics
    ]


@router.put("/impact-metrics/{metric_id}/verify")
def verify_metric(metric_id: int, db: Session = Depends(get_db), _: User = AdminUser):
    metric = db.query(ImpactMetric).filter(ImpactMetric.id == metric_id).first()
    if not metric:
        raise HTTPException(404, "Metric not found")
    metric.verified = True
    db.commit()
    return {"message": "Metric verified"}
