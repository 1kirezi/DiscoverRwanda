from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# ── Learning ────────────────────────────────────────────────────────────────

class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)         # digital_payments | booking_systems | data_analytics
    prerequisites = Column(JSON, default=list)
    skill_tags = Column(JSON, default=list)
    estimated_hours = Column(Integer, default=10)
    difficulty = Column(String(50), default="beginner")
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    modules = relationship("LearningModule", back_populates="path", order_by="LearningModule.order_index")
    badge = relationship("Badge", back_populates="learning_path", uselist=False)
    progress = relationship("LearningProgress", back_populates="path")


class LearningModule(Base):
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    path = relationship("LearningPath", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", order_by="Lesson.order_index")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    content_type = Column(String(50), default="text")   # text | video | interactive
    video_url = Column(String(500), nullable=True)
    order_index = Column(Integer, default=0)
    estimated_minutes = Column(Integer, default=15)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("LearningModule", back_populates="lessons")
    quizzes = relationship("Quiz", back_populates="lesson")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)              # ["Option A", "Option B", ...]
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)

    lesson = relationship("Lesson", back_populates="quizzes")


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=False)
    completed_lesson_ids = Column(JSON, default=list)
    quiz_scores = Column(JSON, default=dict)            # {lesson_id: score}
    percent_complete = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    student = relationship("User", foreign_keys=[student_id])
    path = relationship("LearningPath", back_populates="progress")


# ── Badges ───────────────────────────────────────────────────────────────────

class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    color = Column(String(50), default="#1D9E75")
    badge_type = Column(String(50), default="course")   # course | project | milestone | special
    learning_path_id = Column(Integer, ForeignKey("learning_paths.id"), nullable=True)
    criteria = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    learning_path = relationship("LearningPath", back_populates="badge")
    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime(timezone=True), server_default=func.now())
    awarded_for = Column(String(255), nullable=True)    # "Completed Python for Tourism"

    user = relationship("User", back_populates="earned_badges")
    badge = relationship("Badge", back_populates="user_badges")


# ── Mentorship ────────────────────────────────────────────────────────────────

class MentorProfile(Base):
    __tablename__ = "mentor_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    expertise_areas = Column(JSON, default=list)
    years_experience = Column(Integer, default=0)
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    availability_slots = Column(JSON, default=list)     # [{day, start_time, end_time}, ...]
    max_mentees = Column(Integer, default=3)
    is_available = Column(Boolean, default=True)
    bio = Column(Text, nullable=True)
    rating = Column(Float, default=0.0)
    total_sessions = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    sessions = relationship("MentorSession", back_populates="mentor_profile")


class MentorSession(Base):
    __tablename__ = "mentor_sessions"

    id = Column(Integer, primary_key=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mentor_profile_id = Column(Integer, ForeignKey("mentor_profiles.id"), nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(50), default="scheduled")    # scheduled | completed | cancelled
    objectives = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    student_rating = Column(Integer, nullable=True)     # 1-5
    student_feedback = Column(Text, nullable=True)
    meeting_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="mentor_sessions_as_mentor")
    student = relationship("User", foreign_keys=[student_id], back_populates="mentor_sessions_as_student")
    mentor_profile = relationship("MentorProfile", back_populates="sessions")