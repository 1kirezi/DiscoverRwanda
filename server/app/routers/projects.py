from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.project import Project, Task, Milestone, Message, ImpactMetric
from app.models.challenge import Team, TeamMember
from app.schemas.challenge import (
    ProjectOut, ProjectUpdate,
    TaskCreate, TaskUpdate, TaskOut,
    MilestoneCreate, MilestoneOut,
    MessageCreate, MessageOut,
    ImpactMetricCreate,
)
from app.core.security import get_current_active_user

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


def _check_project_access(project: Project, user: User, db: Session):
    team = db.query(Team).filter(Team.id == project.team_id).first()
    is_member = db.query(TeamMember).filter(
        TeamMember.team_id == team.id,
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    is_business_owner = team.challenge.business_id == user.id
    is_privileged = user.role in [UserRole.ADMIN, UserRole.FACULTY]
    if not (is_member or is_business_owner or is_privileged):
        raise HTTPException(403, "No access to this project")


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int, payload: ProjectUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


# ── Tasks ─────────────────────────────────────────────────────────────────────

@router.get("/{project_id}/tasks", response_model=List[TaskOut])
def list_tasks(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    return db.query(Task).filter(Task.project_id == project_id).all()


@router.post("/{project_id}/tasks", response_model=TaskOut, status_code=201)
def create_task(
    project_id: int, payload: TaskCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    task = Task(project_id=project_id, created_by=current_user.id, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{project_id}/tasks/{task_id}", response_model=TaskOut)
def update_task(
    project_id: int, task_id: int, payload: TaskUpdate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{project_id}/tasks/{task_id}", status_code=204)
def delete_task(
    project_id: int, task_id: int,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
    if not task:
        raise HTTPException(404, "Task not found")
    db.delete(task)
    db.commit()


# ── Milestones ────────────────────────────────────────────────────────────────

@router.get("/{project_id}/milestones", response_model=List[MilestoneOut])
def list_milestones(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()


@router.post("/{project_id}/milestones", response_model=MilestoneOut, status_code=201)
def create_milestone(
    project_id: int, payload: MilestoneCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    ms = Milestone(project_id=project_id, **payload.model_dump())
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms


# ── Messages ──────────────────────────────────────────────────────────────────

@router.get("/{project_id}/messages", response_model=List[MessageOut])
def list_messages(
    project_id: int, skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    msgs = (
        db.query(Message)
        .filter(Message.project_id == project_id)
        .order_by(Message.created_at.desc())
        .offset(skip).limit(limit)
        .all()
    )
    result = []
    for m in msgs:
        out = MessageOut.model_validate(m)
        out.sender_name = m.sender.full_name if m.sender else None
        result.append(out)
    return list(reversed(result))


@router.post("/{project_id}/messages", response_model=MessageOut, status_code=201)
def post_message(
    project_id: int, payload: MessageCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    _check_project_access(project, current_user, db)
    msg = Message(project_id=project_id, sender_id=current_user.id, **payload.model_dump())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    out = MessageOut.model_validate(msg)
    out.sender_name = current_user.full_name
    return out


# ── Impact Metrics ────────────────────────────────────────────────────────────

@router.post("/{project_id}/metrics", status_code=201)
def add_impact_metric(
    project_id: int, payload: ImpactMetricCreate,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(404, "Project not found")
    metric = ImpactMetric(project_id=project_id, reported_by=current_user.id, **payload.model_dump())
    db.add(metric)
    db.commit()
    return {"message": "Metric recorded"}


@router.get("/{project_id}/metrics")
def get_impact_metrics(project_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_active_user)):
    return db.query(ImpactMetric).filter(ImpactMetric.project_id == project_id).all()
