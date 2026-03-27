from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User, UserRole
from app.models.learning import LearningPath, LearningModule, Lesson, Quiz, LearningProgress, Badge, UserBadge
from app.core.security import get_current_active_user, require_role
from app.services.badges import check_and_award_path_badge
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/learning", tags=["Learning"])


class QuizAnswerRequest(BaseModel):
    quiz_id: int
    selected_index: int


class LessonCompleteRequest(BaseModel):
    lesson_id: int
    quiz_answers: Optional[List[QuizAnswerRequest]] = []


@router.get("/paths")
def list_paths(
    domain: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(LearningPath).filter(LearningPath.is_published == True)
    if domain:
        q = q.filter(LearningPath.domain == domain)
    paths = q.all()

    result = []
    for path in paths:
        progress = None
        if current_user.role == UserRole.STUDENT:
            progress = (
                db.query(LearningProgress)
                .filter(LearningProgress.student_id == current_user.id, LearningProgress.path_id == path.id)
                .first()
            )
        result.append({
            "id": path.id,
            "title": path.title,
            "description": path.description,
            "domain": path.domain,
            "difficulty": path.difficulty,
            "estimated_hours": path.estimated_hours,
            "skill_tags": path.skill_tags,
            "modules_count": len(path.modules),
            "progress": progress.percent_complete if progress else 0,
            "is_enrolled": progress is not None,
            "is_completed": progress.is_completed if progress else False,
        })
    return result


@router.get("/paths/recommended")
def recommended_paths(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    profile = current_user.student_profile
    student_skills = set(s.lower() for s in (profile.skills_inventory or [])) if profile else set()
    career_interests = set(i.lower() for i in (profile.career_interests or [])) if profile else set()

    paths = db.query(LearningPath).filter(LearningPath.is_published == True).all()
    scored = []
    for path in paths:
        path_skills = set(s.lower() for s in (path.skill_tags or []))
        overlap = len(path_skills & (student_skills | career_interests))
        scored.append((path, overlap))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [
        {"id": p.id, "title": p.title, "domain": p.domain, "difficulty": p.difficulty,
         "match_score": score, "estimated_hours": p.estimated_hours}
        for p, score in scored[:5]
    ]


@router.get("/paths/{path_id}")
def get_path(path_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(404, "Learning path not found")

    progress = None
    if current_user.role == UserRole.STUDENT:
        progress = db.query(LearningProgress).filter(
            LearningProgress.student_id == current_user.id, LearningProgress.path_id == path_id
        ).first()

    return {
        "id": path.id,
        "title": path.title,
        "description": path.description,
        "domain": path.domain,
        "difficulty": path.difficulty,
        "estimated_hours": path.estimated_hours,
        "skill_tags": path.skill_tags,
        "modules": [
            {
                "id": m.id,
                "title": m.title,
                "order_index": m.order_index,
                "lessons": [
                    {
                        "id": l.id,
                        "title": l.title,
                        "content_type": l.content_type,
                        "estimated_minutes": l.estimated_minutes,
                        "is_completed": l.id in (progress.completed_lesson_ids or []) if progress else False,
                    }
                    for l in m.lessons
                ],
            }
            for m in path.modules
        ],
        "progress": progress.percent_complete if progress else 0,
        "is_enrolled": progress is not None,
        "is_completed": progress.is_completed if progress else False,
    }


@router.post("/paths/{path_id}/enroll")
def enroll(path_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role(UserRole.STUDENT))):
    path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
    if not path:
        raise HTTPException(404, "Learning path not found")
    existing = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id, LearningProgress.path_id == path_id
    ).first()
    if existing:
        return {"message": "Already enrolled"}
    db.add(LearningProgress(student_id=current_user.id, path_id=path_id))
    db.commit()
    return {"message": "Enrolled successfully"}


@router.get("/lessons/{lesson_id}")
def get_lesson(lesson_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return {
        "id": lesson.id,
        "title": lesson.title,
        "content": lesson.content,
        "content_type": lesson.content_type,
        "video_url": lesson.video_url,
        "estimated_minutes": lesson.estimated_minutes,
        "quizzes": [
            {"id": q.id, "question": q.question, "options": q.options}
            for q in lesson.quizzes
        ],
    }


@router.post("/lessons/{lesson_id}/complete")
def complete_lesson(
    lesson_id: int,
    payload: LessonCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    path_id = lesson.module.path_id
    progress = db.query(LearningProgress).filter(
        LearningProgress.student_id == current_user.id, LearningProgress.path_id == path_id
    ).first()
    if not progress:
        raise HTTPException(400, "Enroll in the path first")

    completed = set(progress.completed_lesson_ids or [])
    completed.add(lesson_id)
    progress.completed_lesson_ids = list(completed)

    # Grade quizzes
    quiz_scores = dict(progress.quiz_scores or {})
    correct = 0
    for answer in (payload.quiz_answers or []):
        quiz = db.query(Quiz).filter(Quiz.id == answer.quiz_id).first()
        if quiz:
            is_correct = quiz.correct_index == answer.selected_index
            quiz_scores[str(answer.quiz_id)] = 1 if is_correct else 0
            correct += 1 if is_correct else 0
    progress.quiz_scores = quiz_scores

    # Recalculate percent
    all_lessons = [l for m in lesson.module.path.modules for l in m.lessons]
    progress.percent_complete = round(len(completed) / len(all_lessons) * 100, 1) if all_lessons else 0

    if progress.percent_complete >= 100:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()
        badge = check_and_award_path_badge(db, current_user.id, path_id)
        db.commit()
        return {"message": "Lesson completed — path finished!", "badge_awarded": badge.name if badge else None}

    db.commit()
    return {"message": "Lesson completed", "percent_complete": progress.percent_complete}


@router.get("/badges/mine")
def my_badges(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    badges = db.query(UserBadge).filter(UserBadge.user_id == current_user.id).all()
    return [
        {
            "id": ub.id,
            "badge_id": ub.badge_id,
            "name": ub.badge.name,
            "description": ub.badge.description,
            "icon_url": ub.badge.icon_url,
            "color": ub.badge.color,
            "badge_type": ub.badge.badge_type,
            "awarded_at": ub.awarded_at,
            "awarded_for": ub.awarded_for,
        }
        for ub in badges
    ]
