from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.challenge import ChallengeStatus, DifficultyLevel, TeamStatus
from app.models.project import TaskStatus, MilestoneStatus


# ── Challenge ─────────────────────────────────────────────────────────────────

class ChallengeCreate(BaseModel):
    title: str
    description: str
    problem_statement: Optional[str] = None
    success_criteria: Optional[str] = None
    required_skills: List[str] = []
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    estimated_weeks: int = 8
    max_team_size: int = 4
    category: Optional[str] = None
    location: Optional[str] = None
    is_remote: bool = True
    deadline: Optional[datetime] = None


class ChallengeUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    problem_statement: Optional[str] = None
    success_criteria: Optional[str] = None
    required_skills: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    estimated_weeks: Optional[int] = None
    max_team_size: Optional[int] = None
    category: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    deadline: Optional[datetime] = None


class ChallengeOut(BaseModel):
    id: int
    business_id: int
    title: str
    description: str
    problem_statement: Optional[str]
    success_criteria: Optional[str]
    required_skills: List[str]
    difficulty_level: DifficultyLevel
    estimated_weeks: int
    max_team_size: int
    status: ChallengeStatus
    category: Optional[str]
    location: Optional[str]
    is_remote: bool
    views_count: int
    applications_count: int
    created_at: datetime
    deadline: Optional[datetime]
    business_name: Optional[str] = None
    match_score: Optional[float] = None

    class Config:
        from_attributes = True


class AdminChallengeAction(BaseModel):
    action: str          # approve | reject
    admin_notes: Optional[str] = None


# ── Team ──────────────────────────────────────────────────────────────────────

class TeamCreate(BaseModel):
    challenge_id: int
    name: str
    formation_type: str = "self_organized"


class TeamOut(BaseModel):
    id: int
    challenge_id: int
    name: str
    status: TeamStatus
    formation_type: str
    disciplines_represented: List[str]
    max_members: int
    created_at: datetime
    members: List[dict] = []

    class Config:
        from_attributes = True


class JoinTeamRequest(BaseModel):
    academic_discipline: Optional[str] = None


# ── Project ───────────────────────────────────────────────────────────────────

class ProjectOut(BaseModel):
    id: int
    team_id: int
    challenge_id: int
    title: str
    description: Optional[str]
    status: str
    github_url: Optional[str]
    demo_url: Optional[str]
    tech_stack: List[str]
    start_date: datetime
    end_date: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectUpdate(BaseModel):
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    description: Optional[str] = None


# ── Task ──────────────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    assigned_to: Optional[int]
    priority: str
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Milestone ─────────────────────────────────────────────────────────────────

class MilestoneCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class MilestoneOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    status: MilestoneStatus
    due_date: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ── Message ───────────────────────────────────────────────────────────────────

class MessageCreate(BaseModel):
    content: str
    message_type: str = "text"


class MessageOut(BaseModel):
    id: int
    project_id: int
    sender_id: int
    sender_name: Optional[str] = None
    content: str
    message_type: str
    is_edited: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Impact Metrics ────────────────────────────────────────────────────────────

class ImpactMetricCreate(BaseModel):
    metric_type: str
    value: Optional[str] = None
    description: Optional[str] = None
