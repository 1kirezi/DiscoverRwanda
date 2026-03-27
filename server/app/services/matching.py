"""
Weighted scoring matching algorithm (FR 2.1)

Score components (total = 100):
  - Skills overlap          40 pts
  - Academic program        25 pts
  - Availability            20 pts
  - Past project history    15 pts
"""
from sqlalchemy.orm import Session
from app.models.user import User, StudentProfile
from app.models.challenge import Challenge, MatchScore
from app.models.project import Project
from typing import List
import json


SKILL_WEIGHT       = 0.40
PROGRAM_WEIGHT     = 0.25
AVAILABILITY_WEIGHT = 0.20
HISTORY_WEIGHT     = 0.15

PROGRAM_DOMAIN_MAP = {
    "computer science":     ["tech", "booking_system", "data_analytics", "mobile_app", "api"],
    "software engineering": ["tech", "booking_system", "mobile_app", "api"],
    "data science":         ["data_analytics", "reporting", "insights"],
    "business management":  ["digital_payments", "marketing", "strategy"],
    "entrepreneurship":     ["digital_payments", "marketing", "strategy", "startup"],
    "ux design":            ["mobile_app", "website", "user_experience"],
    "communications":       ["marketing", "content", "social_media"],
}


def _skills_score(student_skills: List[str], required_skills: List[str]) -> float:
    if not required_skills:
        return 1.0
    if not student_skills:
        return 0.0
    student_lower = {s.lower() for s in student_skills}
    required_lower = {s.lower() for s in required_skills}
    overlap = student_lower & required_lower
    return len(overlap) / len(required_lower)


def _program_score(academic_program: str, challenge_category: str) -> float:
    if not academic_program or not challenge_category:
        return 0.5
    program_lower = academic_program.lower()
    category_lower = challenge_category.lower()
    for program_key, domains in PROGRAM_DOMAIN_MAP.items():
        if program_key in program_lower:
            for domain in domains:
                if domain in category_lower:
                    return 1.0
            return 0.4
    return 0.3


def _availability_score(hours_per_week: int, estimated_weeks: int) -> float:
    # Challenge with 8 weeks needs at least 8h/week commitment
    required_weekly = max(4, estimated_weeks // 2)
    if hours_per_week >= required_weekly * 1.5:
        return 1.0
    if hours_per_week >= required_weekly:
        return 0.8
    if hours_per_week >= required_weekly * 0.5:
        return 0.5
    return 0.2


def _history_score(completed_projects: int) -> float:
    if completed_projects == 0:
        return 0.5   # neutral — don't penalise newcomers
    if completed_projects >= 3:
        return 1.0
    return 0.5 + (completed_projects * 0.15)


def compute_match_score(student: StudentProfile, challenge: Challenge) -> dict:
    skills_s   = _skills_score(student.skills_inventory or [], challenge.required_skills or [])
    program_s  = _program_score(student.academic_program or "", challenge.category or "")
    avail_s    = _availability_score(student.availability_hours_per_week or 5, challenge.estimated_weeks or 8)
    history_s  = _history_score(student.completed_projects_count or 0)

    total = (
        skills_s   * SKILL_WEIGHT +
        program_s  * PROGRAM_WEIGHT +
        avail_s    * AVAILABILITY_WEIGHT +
        history_s  * HISTORY_WEIGHT
    ) * 100

    return {
        "total_score":        round(total, 2),
        "skills_score":       round(skills_s * 100, 2),
        "program_score":      round(program_s * 100, 2),
        "availability_score": round(avail_s * 100, 2),
        "history_score":      round(history_s * 100, 2),
    }


def get_matched_challenges(db: Session, student_user_id: int, limit: int = 10) -> List[dict]:
    student_profile = (
        db.query(StudentProfile)
        .filter(StudentProfile.user_id == student_user_id)
        .first()
    )
    if not student_profile:
        return []

    active_challenges = (
        db.query(Challenge)
        .filter(Challenge.status == "active")
        .all()
    )

    results = []
    for challenge in active_challenges:
        scores = compute_match_score(student_profile, challenge)
        # Upsert match score record
        existing = (
            db.query(MatchScore)
            .filter(
                MatchScore.student_id == student_user_id,
                MatchScore.challenge_id == challenge.id
            )
            .first()
        )
        if existing:
            for k, v in scores.items():
                setattr(existing, k, v)
        else:
            db.add(MatchScore(student_id=student_user_id, challenge_id=challenge.id, **scores))

        results.append({"challenge": challenge, **scores})

    db.commit()
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results[:limit]
