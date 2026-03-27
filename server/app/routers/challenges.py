from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.challenge import Challenge, ChallengeStatus, Team, TeamMember, MatchScore
from app.models.project import Project
from app.schemas.challenge import (
    ChallengeCreate, ChallengeUpdate, ChallengeOut,
    TeamCreate, TeamOut, JoinTeamRequest, AdminChallengeAction,
)
from app.core.security import get_current_active_user, require_role
from app.services.matching import get_matched_challenges

router = APIRouter(prefix="/api/v1/challenges", tags=["Challenges"])


def _team_out(team: Team, members: List[dict]) -> TeamOut:
    return TeamOut(
        id=team.id,
        challenge_id=team.challenge_id,
        name=team.name,
        status=team.status,
        formation_type=team.formation_type,
        disciplines_represented=team.disciplines_represented or [],
        max_members=team.max_members,
        created_at=team.created_at,
        members=members,
    )


@router.get("", response_model=List[ChallengeOut])
def list_challenges(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    q = db.query(Challenge)
    if not (current_user.role in [UserRole.ADMIN, UserRole.FACULTY]):
        q = q.filter(Challenge.status == ChallengeStatus.ACTIVE)
    if status:
        q = q.filter(Challenge.status == status)
    if category:
        q = q.filter(Challenge.category == category)
    if difficulty:
        q = q.filter(Challenge.difficulty_level == difficulty)
    if search:
        q = q.filter(Challenge.title.ilike(f"%{search}%"))

    challenges = q.offset(skip).limit(limit).all()
    result = []
    for c in challenges:
        out = ChallengeOut.model_validate(c)
        if c.business_owner and c.business_owner.business_profile:
            out.business_name = c.business_owner.business_profile.business_name
        result.append(out)
    return result


@router.get("/matched", response_model=List[dict])
def get_my_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    matches = get_matched_challenges(db, current_user.id)
    return [
        {
            "challenge": ChallengeOut.model_validate(m["challenge"]).model_dump(),
            "match_score": m["total_score"],
            "score_breakdown": {
                "skills": m["skills_score"],
                "program": m["program_score"],
                "availability": m["availability_score"],
                "history": m["history_score"],
            },
        }
        for m in matches
    ]


@router.get("/{challenge_id}", response_model=ChallengeOut)
def get_challenge(challenge_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    challenge.views_count += 1
    db.commit()
    out = ChallengeOut.model_validate(challenge)
    if challenge.business_owner and challenge.business_owner.business_profile:
        out.business_name = challenge.business_owner.business_profile.business_name
    return out


@router.post("", response_model=ChallengeOut, status_code=201)
def create_challenge(
    payload: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUSINESS)),
):
    if current_user.verification_status.value != "approved":
        raise HTTPException(status_code=403, detail="Business account not yet verified")

    challenge = Challenge(business_id=current_user.id, **payload.model_dump())
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


@router.put("/{challenge_id}", response_model=ChallengeOut)
def update_challenge(
    challenge_id: int,
    payload: ChallengeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(404, "Challenge not found")
    if challenge.business_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(403, "Not authorized")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(challenge, field, value)
    db.commit()
    db.refresh(challenge)
    return challenge


@router.post("/{challenge_id}/review", response_model=ChallengeOut)
def review_challenge(
    challenge_id: int,
    payload: AdminChallengeAction,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(404, "Challenge not found")

    challenge.status = ChallengeStatus.ACTIVE if payload.action == "approve" else ChallengeStatus.REJECTED
    challenge.admin_notes = payload.admin_notes
    db.commit()
    db.refresh(challenge)
    return challenge


# ── Teams ─────────────────────────────────────────────────────────────────────

@router.get("/{challenge_id}/teams", response_model=List[TeamOut])
def list_teams(challenge_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    teams = db.query(Team).filter(Team.challenge_id == challenge_id).all()
    result = []
    for team in teams:
        members = [
            {"user_id": m.user_id, "name": m.user.full_name, "role": m.role_in_team, "discipline": m.academic_discipline}
            for m in team.members if m.is_active
        ]
        result.append(_team_out(team, members))
    return result


@router.post("/{challenge_id}/teams", response_model=TeamOut, status_code=201)
def create_team(
    challenge_id: int,
    payload: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.FACULTY)),
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id, Challenge.status == ChallengeStatus.ACTIVE).first()
    if not challenge:
        raise HTTPException(404, "Active challenge not found")

    team = Team(challenge_id=challenge_id, name=payload.name, formation_type=payload.formation_type)
    db.add(team)
    db.flush()

    discipline = ""
    if current_user.student_profile:
        discipline = current_user.student_profile.academic_program or ""

    member = TeamMember(team_id=team.id, user_id=current_user.id, role_in_team="lead", academic_discipline=discipline)
    team.disciplines_represented = [discipline] if discipline else []
    db.add(member)

    # Auto-create project workspace
    project = Project(team_id=team.id, challenge_id=challenge_id, title=f"Project: {challenge.title}")
    db.add(project)
    db.commit()
    db.refresh(team)

    members = [{"user_id": current_user.id, "name": current_user.full_name, "role": "lead", "discipline": discipline}]
    return _team_out(team, members)


@router.post("/{challenge_id}/teams/{team_id}/join", response_model=TeamOut)
def join_team(
    challenge_id: int,
    team_id: int,
    payload: JoinTeamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    team = db.query(Team).filter(Team.id == team_id, Team.challenge_id == challenge_id).first()
    if not team:
        raise HTTPException(404, "Team not found")

    active_members = [m for m in team.members if m.is_active]
    if len(active_members) >= team.max_members:
        raise HTTPException(400, "Team is full")

    already_member = any(m.user_id == current_user.id for m in active_members)
    if already_member:
        raise HTTPException(400, "Already a team member")

    discipline = payload.academic_discipline or (
        current_user.student_profile.academic_program if current_user.student_profile else ""
    ) or ""

    # BR 7: enforce at least 2 disciplines
    current_disciplines = set(team.disciplines_represented or [])
    current_disciplines.add(discipline)
    team.disciplines_represented = list(current_disciplines)

    db.add(TeamMember(team_id=team_id, user_id=current_user.id, role_in_team="member", academic_discipline=discipline))
    db.commit()
    db.refresh(team)

    members = [
        {"user_id": m.user_id, "name": m.user.full_name, "role": m.role_in_team, "discipline": m.academic_discipline}
        for m in team.members if m.is_active
    ]
    return _team_out(team, members)
