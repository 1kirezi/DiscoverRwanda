from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    STUDENT = "student"
    BUSINESS = "business"
    FACULTY = "faculty"
    ADMIN = "admin"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        Enum(
            UserRole,
            native_enum=False,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        nullable=False,
    )
    is_active = Column(Boolean, default=True)
    is_email_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    verification_status = Column(
        Enum(
            VerificationStatus,
            native_enum=False,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
        ),
        default=VerificationStatus.NOT_REQUIRED,
    )
    verification_documents = Column(JSON, nullable=True)
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    business_profile = relationship("BusinessProfile", back_populates="user", uselist=False)
    faculty_profile = relationship("FacultyProfile", back_populates="user", uselist=False)
    submitted_challenges = relationship("Challenge", back_populates="business_owner")
    team_memberships = relationship("TeamMember", back_populates="user")
    earned_badges = relationship("UserBadge", back_populates="user")
    sent_messages = relationship("Message", back_populates="sender")
    mentor_sessions_as_mentor = relationship("MentorSession", foreign_keys="MentorSession.mentor_id", back_populates="mentor")
    mentor_sessions_as_student = relationship("MentorSession", foreign_keys="MentorSession.student_id", back_populates="student")


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    academic_program = Column(String(255), nullable=True)
    year_of_study = Column(Integer, nullable=True)
    skills_inventory = Column(JSON, default=list)   # ["Python", "React", ...]
    career_interests = Column(JSON, default=list)
    availability_hours_per_week = Column(Integer, default=10)
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_summary = Column(Text, nullable=True)
    completed_projects_count = Column(Integer, default=0)
    total_badges = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="student_profile")
    learning_progress = relationship(
        "LearningProgress",
        primaryjoin="StudentProfile.user_id == foreign(LearningProgress.student_id)",
        viewonly=True,
    )
    mentor_sessions = relationship(
        "MentorSession",
        primaryjoin="StudentProfile.user_id == foreign(MentorSession.student_id)",
        viewonly=True,
    )


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String(255), nullable=False)
    business_type = Column(String(100), nullable=True)   # lodge, tour_operator, hotel, etc.
    size = Column(String(50), nullable=True)              # small, medium, large
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    technology_needs = Column(JSON, default=list)
    partnership_level = Column(String(50), default="basic")
    subscription_tier = Column(String(50), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="business_profile")


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    department = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    assigned_student_ids = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="faculty_profile")