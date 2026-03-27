from sqlalchemy.orm import Session
from app.models.learning import Badge, UserBadge, LearningProgress
from app.models.user import StudentProfile


def award_badge(db: Session, user_id: int, badge_id: int, reason: str = "") -> bool:
    existing = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
        .first()
    )
    if existing:
        return False   # already earned

    db.add(UserBadge(user_id=user_id, badge_id=badge_id, awarded_for=reason))
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user_id).first()
    if profile:
        profile.total_badges = (profile.total_badges or 0) + 1
    db.commit()
    return True


def check_and_award_path_badge(db: Session, user_id: int, path_id: int):
    progress = (
        db.query(LearningProgress)
        .filter(
            LearningProgress.student_id == user_id,
            LearningProgress.path_id == path_id,
            LearningProgress.is_completed == True,
        )
        .first()
    )
    if not progress:
        return None

    badge = db.query(Badge).filter(Badge.learning_path_id == path_id).first()
    if badge:
        awarded = award_badge(db, user_id, badge.id, f"Completed learning path #{path_id}")
        if awarded:
            return badge
    return None


def award_project_completion_badge(db: Session, user_id: int, project_id: int):
    badge = db.query(Badge).filter(Badge.badge_type == "project").first()
    if badge:
        award_badge(db, user_id, badge.id, f"Completed project #{project_id}")
