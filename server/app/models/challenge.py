from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


def _enum_values(enum_cls):
    return [member.value for member in enum_cls]


class ChallengeStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ACTIVE = "active"
    COMPLETED = "completed"
    REJECTED = "rejected"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TeamStatus(str, enum.Enum):
    FORMING = "forming"
    ACTIVE = "active"
    COMPLETED = "completed"
    DISBANDED = "disbanded"


class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    problem_statement = Column(Text, nullable=True)
    success_criteria = Column(Text, nullable=True)
    required_skills = Column(JSON, default=list)      # ["Python", "Data Analysis", ...]
    difficulty_level = Column(
        Enum(DifficultyLevel, native_enum=False, values_callable=_enum_values),
        default=DifficultyLevel.INTERMEDIATE,
    )
    estimated_weeks = Column(Integer, default=8)
    max_team_size = Column(Integer, default=4)
    status = Column(
        Enum(ChallengeStatus, native_enum=False, values_callable=_enum_values),
        default=ChallengeStatus.DRAFT,
    )
    category = Column(String(100), nullable=True)     # "digital_payments", "booking_system", etc.
    location = Column(String(255), nullable=True)
    is_remote = Column(Boolean, default=True)
    attachments = Column(JSON, default=list)
    admin_notes = Column(Text, nullable=True)
    views_count = Column(Integer, default=0)
    applications_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deadline = Column(DateTime(timezone=True), nullable=True)

    business_owner = relationship("User", back_populates="submitted_challenges")
    teams = relationship("Team", back_populates="challenge")
    tags = relationship("ChallengeTag", back_populates="challenge")


class ChallengeTag(Base):
    __tablename__ = "challenge_tags"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    tag = Column(String(100), nullable=False)
    tag_type = Column(String(50), default="skill")    # skill | category | technology

    challenge = relationship("Challenge", back_populates="tags")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(
        Enum(TeamStatus, native_enum=False, values_callable=_enum_values),
        default=TeamStatus.FORMING,
    )
    formation_type = Column(String(50), default="self_organized")  # self_organized | instructor_assigned
    disciplines_represented = Column(JSON, default=list)  # ["Computer Science", "Business", ...]
    max_members = Column(Integer, default=4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    challenge = relationship("Challenge", back_populates="teams")
    members = relationship("TeamMember", back_populates="team")
    project = relationship("Project", back_populates="team", uselist=False)


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_in_team = Column(String(100), default="member")   # lead | member
    academic_discipline = Column(String(255), nullable=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_memberships")


class MatchScore(Base):
    __tablename__ = "match_scores"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    total_score = Column(Float, default=0.0)
    skills_score = Column(Float, default=0.0)
    program_score = Column(Float, default=0.0)
    availability_score = Column(Float, default=0.0)
    history_score = Column(Float, default=0.0)
    is_applied = Column(Boolean, default=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())