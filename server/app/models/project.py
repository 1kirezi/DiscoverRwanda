from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class MilestoneStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), unique=True, nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    github_url = Column(String(500), nullable=True)
    demo_url = Column(String(500), nullable=True)
    tech_stack = Column(JSON, default=list)
    outcomes = Column(JSON, default=dict)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    team = relationship("Team", back_populates="project")
    tasks = relationship("Task", back_populates="project")
    milestones = relationship("Milestone", back_populates="project")
    files = relationship("ProjectFile", back_populates="project")
    messages = relationship("Message", back_populates="project")
    impact_metrics = relationship("ImpactMetric", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus, native_enum=False), default=TaskStatus.TODO)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    priority = Column(String(20), default="medium")   # low | medium | high
    due_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(MilestoneStatus, native_enum=False), default=MilestoneStatus.UPCOMING)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="milestones")


class ProjectFile(Base):
    __tablename__ = "project_files"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_url = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="files")
    uploader = relationship("User")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")   # text | system | file
    msg_metadata = Column(JSON, nullable=True)
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")


class ImpactMetric(Base):
    __tablename__ = "impact_metrics"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    metric_type = Column(String(100), nullable=False)  # revenue_increase | cost_reduction | efficiency_gain
    value = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    reported_at = Column(DateTime(timezone=True), server_default=func.now())

    project = relationship("Project", back_populates="impact_metrics")
    reporter = relationship("User")