from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os, uuid, aiofiles
from app.database import get_db
from app.models.user import User, UserRole, VerificationStatus, StudentProfile, BusinessProfile
from app.models.challenge import Team, TeamMember
from app.models.project import Project
from app.models.learning import UserBadge, LearningProgress
from app.schemas.user import UserOut, UserUpdate, StudentProfileUpdate, BusinessProfileUpdate, VerificationRequest
from app.core.security import get_current_active_user, require_role
from app.config import settings

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me/portfolio")
def get_my_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    profile = current_user.student_profile
    memberships = db.query(TeamMember).filter(
        TeamMember.user_id == current_user.id, TeamMember.is_active == True
    ).all()

    projects = []
    for m in memberships:
        team = m.team
        if team and team.project:
            p = team.project
            projects.append({
                "project_id": p.id,
                "title": p.title,
                "challenge_title": team.challenge.title if team.challenge else None,
                "status": p.status,
                "role_in_team": m.role_in_team,
                "tech_stack": p.tech_stack,
                "github_url": p.github_url,
                "demo_url": p.demo_url,
                "start_date": p.start_date,
                "end_date": p.end_date,
            })

    badges = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    badge_list = [
        {
            "name": ub.badge.name,
            "icon_url": ub.badge.icon_url,
            "color": ub.badge.color,
            "badge_type": ub.badge.badge_type,
            "awarded_at": ub.awarded_at,
            "awarded_for": ub.awarded_for,
        }
        for ub in badges
    ]

    learning = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id, LearningProgress.is_completed == True
    ).all()
    completed_paths = [
        {"path_id": lp.path_id, "title": lp.path.title, "completed_at": lp.completed_at}
        for lp in learning
    ]

    return {
        "user": UserOut.model_validate(current_user),
        "profile": {
            "academic_program": profile.academic_program if profile else None,
            "year_of_study": profile.year_of_study if profile else None,
            "skills_inventory": profile.skills_inventory if profile else [],
            "career_interests": profile.career_interests if profile else [],
            "linkedin_url": profile.linkedin_url if profile else None,
            "github_url": profile.github_url if profile else None,
            "portfolio_summary": profile.portfolio_summary if profile else None,
        },
        "projects": projects,
        "badges": badge_list,
        "completed_learning_paths": completed_paths,
        "stats": {
            "total_projects": len(projects),
            "total_badges": len(badge_list),
            "completed_paths": len(completed_paths),
            "skills_count": len(profile.skills_inventory or []) if profile else 0,
        },
    }


@router.get("/{user_id}/portfolio")
def get_public_portfolio(user_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.STUDENT).first()
    if not user:
        raise HTTPException(404, "Student not found")
    profile = user.student_profile
    badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    return {
        "user": {"id": user.id, "full_name": user.full_name, "avatar_url": user.avatar_url, "bio": user.bio},
        "academic_program": profile.academic_program if profile else None,
        "skills": profile.skills_inventory if profile else [],
        "badges": [{"name": ub.badge.name, "color": ub.badge.color, "icon_url": ub.badge.icon_url} for ub in badges],
        "linkedin_url": profile.linkedin_url if profile else None,
        "github_url": profile.github_url if profile else None,
    }


@router.put("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/me/student-profile")
def update_student_profile(
    payload: StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    profile = current_user.student_profile
    if not profile:
        raise HTTPException(404, "Profile not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    return {"message": "Profile updated"}


@router.put("/me/business-profile")
def update_business_profile(
    payload: BusinessProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUSINESS)),
):
    profile = current_user.business_profile
    if not profile:
        raise HTTPException(404, "Profile not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    db.commit()
    return {"message": "Profile updated"}


@router.post("/me/verify-business")
def submit_verification(
    payload: VerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUSINESS)),
):
    current_user.verification_status = VerificationStatus.PENDING
    current_user.verification_documents = payload.documents
    db.commit()
    return {"message": "Verification documents submitted. Pending admin review."}


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Only JPEG, PNG, WebP images allowed")
    ext = file.filename.split(".")[-1]
    filename = f"avatars/{uuid.uuid4()}.{ext}"
    os.makedirs(f"{settings.UPLOAD_DIR}/avatars", exist_ok=True)
    async with aiofiles.open(f"{settings.UPLOAD_DIR}/{filename}", "wb") as f:
        await f.write(await file.read())
    current_user.avatar_url = f"/uploads/{filename}"
    db.commit()
    return {"avatar_url": current_user.avatar_url}
