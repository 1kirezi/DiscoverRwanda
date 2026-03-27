"""
Seed script — populates the DB with realistic demo data.
Run: python scripts/seed.py
"""
import sys, os
# Use abspath to guarantee a single canonical path — prevents the Windows
# double-registration bug where the same .py loads under two module identities.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine

# Load model modules first using their canonical names
import app.models.user
import app.models.challenge
import app.models.project
import app.models.learning

from app.models.user import User, UserRole, VerificationStatus, StudentProfile, BusinessProfile, FacultyProfile
from app.models.challenge import Challenge, ChallengeStatus, DifficultyLevel, Team, TeamMember
from app.models.project import Project, Task, Milestone, TaskStatus
from app.models.learning import (
    LearningPath, LearningModule, Lesson, Quiz, LearningProgress,
    Badge, UserBadge, MentorProfile, MentorSession,
)
from app.core.security import hash_password
from datetime import datetime, timedelta
from sqlalchemy import text

Base.metadata.create_all(bind=engine)
db = SessionLocal()


def clear():
    # Backward-compat cleanup: if old job-board tables still exist in a persisted
    # DB volume, clear them first so FK constraints don't block deleting users.
    db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
    db.execute(text("DROP TABLE IF EXISTS job_applications"))
    db.execute(text("DROP TABLE IF EXISTS job_postings"))
    db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    db.commit()

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    print("Cleared existing data.")


def seed():
    clear()

    # ── Admin ─────────────────────────────────────────────────────────────────
    admin = User(email="admin@discoverrwanda.com", password_hash=hash_password("Admin@1234"),
                 full_name="Platform Admin", role=UserRole.ADMIN,
                 verification_status=VerificationStatus.NOT_REQUIRED, is_email_verified=True)
    db.add(admin)

    # ── Faculty ───────────────────────────────────────────────────────────────
    faculty = User(email="faculty@alu.edu", password_hash=hash_password("Faculty@1234"),
                   full_name="Dr. Amara Diallo", role=UserRole.FACULTY,
                   verification_status=VerificationStatus.NOT_REQUIRED, is_email_verified=True)
    db.add(faculty)
    db.flush()
    db.add(FacultyProfile(user_id=faculty.id, department="Technology", specialization="Software Engineering"))

    # ── Students ──────────────────────────────────────────────────────────────
    students_data = [
        ("alice@example.com", "Alice Uwimana", "Computer Science", 2,
         ["Python", "React", "Data Analysis", "REST APIs"], ["Tourism Tech", "Data"]),
        ("bob@example.com", "Bob Nkurunziza", "Business Management", 3,
         ["Excel", "Market Research", "Digital Marketing", "Presentation"], ["Marketing", "Strategy"]),
        ("chloe@example.com", "Chloe Irakoze", "UX Design", 2,
         ["Figma", "User Research", "Prototyping", "CSS"], ["User Experience", "Mobile Apps"]),
        ("david@example.com", "David Mugisha", "Data Science", 4,
         ["Python", "SQL", "Machine Learning", "Tableau"], ["Data Analytics", "Insights"]),
        ("eve@example.com", "Eve Habimana", "Entrepreneurship", 1,
         ["Business Planning", "Marketing", "Communication"], ["Startups", "Tourism"]),
    ]
    student_users = []
    for email, name, program, year, skills, interests in students_data:
        u = User(email=email, password_hash=hash_password("Student@1234"),
                 full_name=name, role=UserRole.STUDENT,
                 verification_status=VerificationStatus.NOT_REQUIRED, is_email_verified=True)
        db.add(u)
        db.flush()
        db.add(StudentProfile(user_id=u.id, academic_program=program, year_of_study=year,
                               skills_inventory=skills, career_interests=interests,
                               availability_hours_per_week=10 + year * 2))
        student_users.append(u)

    # ── Businesses ────────────────────────────────────────────────────────────
    businesses_data = [
        ("kigali@safarilodge.rw", "Safari Lodge Kigali", "Kigali Safari Lodge",
         "lodge", "small", "Rwanda", "Kigali",
         ["booking_system", "digital_payments", "website"]),
        ("info@visitrwanda.rw", "Visit Rwanda Tours", "Visit Rwanda Tours Ltd",
         "tour_operator", "medium", "Rwanda", "Kigali",
         ["mobile_app", "data_analytics", "marketing"]),
        ("tech@akagerugarden.rw", "Akagera Garden Hotel", "Akagera Garden Hotel",
         "hotel", "large", "Rwanda", "Musanze",
         ["data_analytics", "booking_system", "digital_payments"]),
    ]
    business_users = []
    for email, name, biz_name, btype, size, country, city, needs in businesses_data:
        u = User(email=email, password_hash=hash_password("Business@1234"),
                 full_name=name, role=UserRole.BUSINESS,
                 verification_status=VerificationStatus.APPROVED, is_email_verified=True)
        db.add(u)
        db.flush()
        db.add(BusinessProfile(user_id=u.id, business_name=biz_name, business_type=btype,
                                size=size, country=country, city=city, technology_needs=needs))
        business_users.append(u)

    # ── Challenges ────────────────────────────────────────────────────────────
    challenges_data = [
        {
            "title": "Build a Mobile Booking App for Safari Lodge",
            "description": "Develop a mobile-first booking application for our safari lodge. Guests should be able to browse rooms, check availability, and make reservations with M-Pesa integration.",
            "problem_statement": "Our current booking process is entirely manual via phone calls, causing booking conflicts and lost revenue.",
            "success_criteria": "Working mobile app with real-time availability, M-Pesa payment integration, and admin dashboard.",
            "required_skills": ["React", "REST APIs", "Python", "MySQL"],
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "estimated_weeks": 10,
            "category": "booking_system",
            "max_team_size": 4,
            "is_remote": True,
            "status": ChallengeStatus.ACTIVE,
        },
        {
            "title": "Tourism Data Analytics Dashboard",
            "description": "Create a data analytics platform that helps our tour company understand visitor patterns, peak seasons, and revenue trends using historical booking data.",
            "problem_statement": "We have 3 years of booking data in spreadsheets but no way to visualize or act on insights.",
            "success_criteria": "Interactive dashboard with 5+ KPI widgets, seasonal trend analysis, and exportable reports.",
            "required_skills": ["Python", "SQL", "Data Analysis", "Tableau"],
            "difficulty_level": DifficultyLevel.INTERMEDIATE,
            "estimated_weeks": 8,
            "category": "data_analytics",
            "max_team_size": 3,
            "is_remote": True,
            "status": ChallengeStatus.ACTIVE,
        },
        {
            "title": "Digital Payments Integration for Hotel",
            "description": "Integrate multiple African payment methods (M-Pesa, Airtel Money, card payments) into our hotel management system.",
            "problem_statement": "We lose international guests because we only accept cash. Local guests prefer mobile money.",
            "success_criteria": "Working payment gateway supporting at least 3 payment methods with transaction reporting.",
            "required_skills": ["Python", "REST APIs", "Digital Marketing"],
            "difficulty_level": DifficultyLevel.ADVANCED,
            "estimated_weeks": 12,
            "category": "digital_payments",
            "max_team_size": 4,
            "is_remote": False,
            "status": ChallengeStatus.ACTIVE,
        },
        {
            "title": "UX Redesign of Tourism Booking Website",
            "description": "Redesign and rebuild our tour operator website with a focus on mobile experience, fast load times, and improved conversion rates.",
            "problem_statement": "Our website has a 78% bounce rate on mobile. Most visitors leave before completing a booking.",
            "success_criteria": "New website with <3s load time on 3G, >40% mobile conversion improvement, and user testing evidence.",
            "required_skills": ["Figma", "React", "User Research", "CSS"],
            "difficulty_level": DifficultyLevel.BEGINNER,
            "estimated_weeks": 6,
            "category": "website",
            "max_team_size": 3,
            "is_remote": True,
            "status": ChallengeStatus.SUBMITTED,
        },
    ]
    challenge_objects = []
    for i, c_data in enumerate(challenges_data):
        c = Challenge(business_id=business_users[i % len(business_users)].id, **c_data)
        db.add(c)
        challenge_objects.append(c)

    db.flush()

    # ── Team + Project ────────────────────────────────────────────────────────
    team = Team(challenge_id=challenge_objects[0].id, name="BookingWave",
                formation_type="self_organized", max_members=4,
                disciplines_represented=["Computer Science", "Business Management"])
    db.add(team)
    db.flush()

    for i, (student, role) in enumerate(zip(student_users[:3], ["lead", "member", "member"])):
        discipline = student.student_profile.academic_program if student.student_profile else ""
        db.add(TeamMember(team_id=team.id, user_id=student.id, role_in_team=role, academic_discipline=discipline))

    project = Project(
        team_id=team.id, challenge_id=challenge_objects[0].id,
        title="Mobile Booking App — BookingWave",
        description="Full-stack mobile booking solution with M-Pesa integration",
        tech_stack=["React Native", "FastAPI", "MySQL", "M-Pesa API"],
        github_url="https://github.com/example/bookingwave",
    )
    db.add(project)
    db.flush()

    for title, status in [
        ("Setup project repo & dev environment", TaskStatus.DONE),
        ("Design database schema", TaskStatus.DONE),
        ("Build REST API endpoints", TaskStatus.IN_PROGRESS),
        ("Implement M-Pesa integration", TaskStatus.TODO),
        ("Build React Native UI", TaskStatus.TODO),
    ]:
        db.add(Task(project_id=project.id, title=title, status=status, created_by=student_users[0].id))

    for title, due_offset, done in [
        ("Requirements & Design Complete", 14, True),
        ("Backend API Ready", 35, False),
        ("Frontend MVP", 56, False),
        ("Payment Integration", 70, False),
        ("Testing & Deployment", 84, False),
    ]:
        db.add(Milestone(project_id=project.id, title=title,
                          due_date=datetime.utcnow() + timedelta(days=due_offset),
                          status="completed" if done else "upcoming",
                          completed_at=datetime.utcnow() - timedelta(days=3) if done else None))

    # ── Learning Paths ────────────────────────────────────────────────────────
    paths_data = [
        {
            "title": "Tourism Tech Fundamentals",
            "description": "Essential digital skills for Africa's tourism sector — APIs, databases, and cloud basics.",
            "domain": "fundamentals",
            "difficulty": "beginner",
            "estimated_hours": 8,
            "skill_tags": ["REST APIs", "databases", "cloud", "tourism"],
        },
        {
            "title": "Digital Payments for Africa",
            "description": "Implement M-Pesa, Airtel Money, Flutterwave, and card payments in tourism apps.",
            "domain": "digital_payments",
            "difficulty": "intermediate",
            "estimated_hours": 12,
            "skill_tags": ["Python", "REST APIs", "M-Pesa", "digital_payments"],
        },
        {
            "title": "Data Analytics for Tourism",
            "description": "Transform raw booking data into actionable insights using Python, SQL, and visualisation tools.",
            "domain": "data_analytics",
            "difficulty": "intermediate",
            "estimated_hours": 15,
            "skill_tags": ["Python", "SQL", "data_analytics", "Tableau"],
        },
        {
            "title": "Mobile-First Booking Systems",
            "description": "Build responsive, offline-capable booking apps tailored for African mobile-first users.",
            "domain": "booking_system",
            "difficulty": "advanced",
            "estimated_hours": 20,
            "skill_tags": ["React", "REST APIs", "booking_system", "mobile_app"],
        },
    ]
    path_objects = []
    for p_data in paths_data:
        path = LearningPath(**p_data)
        db.add(path)
        db.flush()

        # Modules + lessons
        for m_idx in range(2):
            module = LearningModule(path_id=path.id, title=f"Module {m_idx+1}", order_index=m_idx)
            db.add(module)
            db.flush()
            for l_idx in range(3):
                lesson = Lesson(
                    module_id=module.id,
                    title=f"Lesson {l_idx+1}: {path.title}",
                    content=f"Content for lesson {l_idx+1} of {path.title}. This covers key concepts and practical examples relevant to Africa's tourism sector.",
                    content_type="text",
                    estimated_minutes=20,
                    order_index=l_idx,
                )
                db.add(lesson)
                db.flush()
                db.add(Quiz(
                    lesson_id=lesson.id,
                    question=f"What is the primary benefit of {path.domain} in tourism?",
                    options=["Improved efficiency", "Cost reduction", "Better customer experience", "All of the above"],
                    correct_index=3,
                    explanation="All three benefits apply when implementing digital solutions in tourism.",
                ))

        badge = Badge(
            name=f"{path.title} Certificate",
            description=f"Awarded for completing {path.title}",
            color="#1D9E75",
            badge_type="course",
            learning_path_id=path.id,
        )
        db.add(badge)
        path_objects.append(path)

    db.flush()

    # Add project completion badge
    db.add(Badge(name="Project Champion", description="Completed a tourism technology project",
                 color="#534AB7", badge_type="project"))

    # Enroll first student in first path with progress
    db.add(LearningProgress(
        student_id=student_users[0].id, path_id=path_objects[0].id,
        completed_lesson_ids=[1, 2, 3], percent_complete=50.0,
    ))

    # ── Mentors ───────────────────────────────────────────────────────────────
    mentors_data = [
        ("mentor1@tourismtech.rw", "Jean-Paul Bizimana", "Payment Systems", "FinTech Africa", "CTO"),
        ("mentor2@tourismtech.rw", "Sarah Kamau", "Data Analytics", "RDB Digital", "Data Lead"),
        ("mentor3@tourismtech.rw", "Emmanuel Nkusi", "Mobile Development", "Andela Rwanda", "Senior Engineer"),
    ]
    for email, name, expertise, company, title in mentors_data:
        u = User(email=email, password_hash=hash_password("Mentor@1234"),
                 full_name=name, role=UserRole.FACULTY,
                 verification_status=VerificationStatus.NOT_REQUIRED, is_email_verified=True)
        db.add(u)
        db.flush()
        db.add(FacultyProfile(user_id=u.id))
        db.add(MentorProfile(
            user_id=u.id, expertise_areas=[expertise, "Tourism Technology"],
            company=company, job_title=title, years_experience=7, max_mentees=3,
        ))

    db.commit()
    print("✅ Seed complete!")
    print("\nDemo accounts:")
    print("  Admin:    admin@discoverrwanda.com  / Admin@1234")
    print("  Faculty:  faculty@alu.edu           / Faculty@1234")
    print("  Students: alice@example.com         / Student@1234")
    print("            bob@example.com           / Student@1234")
    print("  Business: kigali@safarilodge.rw     / Business@1234")
    print("  Mentor:   mentor1@tourismtech.rw    / Mentor@1234")


if __name__ == "__main__":
    seed()