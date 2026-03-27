"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('student', 'business', 'faculty', 'admin', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('verification_status', sa.Enum('pending', 'approved', 'rejected', 'not_required', name='verificationstatus'), nullable=True),
        sa.Column('verification_documents', sa.JSON(), nullable=True),
        sa.Column('preferred_language', sa.String(10), nullable=True, default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'])

    # student_profiles
    op.create_table('student_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('academic_program', sa.String(255), nullable=True),
        sa.Column('year_of_study', sa.Integer(), nullable=True),
        sa.Column('skills_inventory', sa.JSON(), nullable=True),
        sa.Column('career_interests', sa.JSON(), nullable=True),
        sa.Column('availability_hours_per_week', sa.Integer(), nullable=True, default=10),
        sa.Column('linkedin_url', sa.String(500), nullable=True),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('portfolio_summary', sa.Text(), nullable=True),
        sa.Column('completed_projects_count', sa.Integer(), nullable=True, default=0),
        sa.Column('total_badges', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # business_profiles
    op.create_table('business_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(255), nullable=False),
        sa.Column('business_type', sa.String(100), nullable=True),
        sa.Column('size', sa.String(50), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('technology_needs', sa.JSON(), nullable=True),
        sa.Column('partnership_level', sa.String(50), nullable=True, default='basic'),
        sa.Column('subscription_tier', sa.String(50), nullable=True, default='free'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # faculty_profiles
    op.create_table('faculty_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('department', sa.String(255), nullable=True),
        sa.Column('specialization', sa.String(255), nullable=True),
        sa.Column('assigned_student_ids', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # challenges
    op.create_table('challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('problem_statement', sa.Text(), nullable=True),
        sa.Column('success_criteria', sa.Text(), nullable=True),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('difficulty_level', sa.Enum('beginner', 'intermediate', 'advanced', name='difficultylevel'), nullable=True),
        sa.Column('estimated_weeks', sa.Integer(), nullable=True, default=8),
        sa.Column('max_team_size', sa.Integer(), nullable=True, default=4),
        sa.Column('status', sa.Enum('draft', 'submitted', 'under_review', 'approved', 'active', 'completed', 'rejected', name='challengestatus'), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('is_remote', sa.Boolean(), nullable=True, default=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('views_count', sa.Integer(), nullable=True, default=0),
        sa.Column('applications_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_challenges_id', 'challenges', ['id'])

    # challenge_tags
    op.create_table('challenge_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('tag', sa.String(100), nullable=False),
        sa.Column('tag_type', sa.String(50), nullable=True, default='skill'),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # teams
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum('forming', 'active', 'completed', 'disbanded', name='teamstatus'), nullable=True),
        sa.Column('formation_type', sa.String(50), nullable=True, default='self_organized'),
        sa.Column('disciplines_represented', sa.JSON(), nullable=True),
        sa.Column('max_members', sa.Integer(), nullable=True, default=4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_teams_id', 'teams', ['id'])

    # team_members
    op.create_table('team_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_in_team', sa.String(100), nullable=True, default='member'),
        sa.Column('academic_discipline', sa.String(255), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # match_scores
    op.create_table('match_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('total_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('skills_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('program_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('availability_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('history_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_applied', sa.Boolean(), nullable=True, default=False),
        sa.Column('computed_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # projects
    op.create_table('projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, default='active'),
        sa.Column('github_url', sa.String(500), nullable=True),
        sa.Column('demo_url', sa.String(500), nullable=True),
        sa.Column('tech_stack', sa.JSON(), nullable=True),
        sa.Column('outcomes', sa.JSON(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id']),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id'),
    )
    op.create_index('ix_projects_id', 'projects', ['id'])

    # tasks
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('todo', 'in_progress', 'in_review', 'done', name='taskstatus'), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(20), nullable=True, default='medium'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # milestones
    op.create_table('milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('upcoming', 'in_progress', 'completed', 'overdue', name='milestonestatus'), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # project_files
    op.create_table('project_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # messages
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(50), nullable=True, default='text'),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_edited', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # impact_metrics
    op.create_table('impact_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('reported_by', sa.Integer(), nullable=False),
        sa.Column('metric_type', sa.String(100), nullable=False),
        sa.Column('value', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('reported_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.ForeignKeyConstraint(['reported_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # learning_paths
    op.create_table('learning_paths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(100), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=True),
        sa.Column('skill_tags', sa.JSON(), nullable=True),
        sa.Column('estimated_hours', sa.Integer(), nullable=True, default=10),
        sa.Column('difficulty', sa.String(50), nullable=True, default='beginner'),
        sa.Column('is_published', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_learning_paths_id', 'learning_paths', ['id'])

    # learning_modules
    op.create_table('learning_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # lessons
    op.create_table('lessons',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_type', sa.String(50), nullable=True, default='text'),
        sa.Column('video_url', sa.String(500), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True, default=0),
        sa.Column('estimated_minutes', sa.Integer(), nullable=True, default=15),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['module_id'], ['learning_modules.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # quizzes
    op.create_table('quizzes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lesson_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=False),
        sa.Column('correct_index', sa.Integer(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # learning_progress
    op.create_table('learning_progress',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('path_id', sa.Integer(), nullable=False),
        sa.Column('completed_lesson_ids', sa.JSON(), nullable=True),
        sa.Column('quiz_scores', sa.JSON(), nullable=True),
        sa.Column('percent_complete', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_completed', sa.Boolean(), nullable=True, default=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['path_id'], ['learning_paths.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # badges
    op.create_table('badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon_url', sa.String(500), nullable=True),
        sa.Column('color', sa.String(50), nullable=True, default='#1D9E75'),
        sa.Column('badge_type', sa.String(50), nullable=True, default='course'),
        sa.Column('learning_path_id', sa.Integer(), nullable=True),
        sa.Column('criteria', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['learning_path_id'], ['learning_paths.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_badges_id', 'badges', ['id'])

    # user_badges
    op.create_table('user_badges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('badge_id', sa.Integer(), nullable=False),
        sa.Column('awarded_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('awarded_for', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['badge_id'], ['badges.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # mentor_profiles
    op.create_table('mentor_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('expertise_areas', sa.JSON(), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True, default=0),
        sa.Column('company', sa.String(255), nullable=True),
        sa.Column('job_title', sa.String(255), nullable=True),
        sa.Column('availability_slots', sa.JSON(), nullable=True),
        sa.Column('max_mentees', sa.Integer(), nullable=True, default=3),
        sa.Column('is_available', sa.Boolean(), nullable=True, default=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True, default=0.0),
        sa.Column('total_sessions', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    # mentor_sessions
    op.create_table('mentor_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mentor_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('mentor_profile_id', sa.Integer(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True, default=60),
        sa.Column('status', sa.String(50), nullable=True, default='scheduled'),
        sa.Column('objectives', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('student_rating', sa.Integer(), nullable=True),
        sa.Column('student_feedback', sa.Text(), nullable=True),
        sa.Column('meeting_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['mentor_id'], ['users.id']),
        sa.ForeignKeyConstraint(['mentor_profile_id'], ['mentor_profiles.id']),
        sa.ForeignKeyConstraint(['student_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # job_postings
    op.create_table('job_postings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('posted_by', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('company', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=True, default='full_time'),
        sa.Column('location', sa.String(255), nullable=True),
        sa.Column('is_remote', sa.Boolean(), nullable=True, default=False),
        sa.Column('required_skills', sa.JSON(), nullable=True),
        sa.Column('salary_range', sa.String(100), nullable=True),
        sa.Column('application_url', sa.String(500), nullable=True),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['posted_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_job_postings_id', 'job_postings', ['id'])

    # job_applications
    op.create_table('job_applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.Integer(), nullable=False),
        sa.Column('applicant_id', sa.Integer(), nullable=False),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True, default='applied'),
        sa.Column('applied_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['applicant_id'], ['users.id']),
        sa.ForeignKeyConstraint(['job_id'], ['job_postings.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    for table in [
        'job_applications', 'job_postings', 'mentor_sessions', 'mentor_profiles',
        'user_badges', 'badges', 'learning_progress', 'quizzes', 'lessons',
        'learning_modules', 'learning_paths', 'impact_metrics', 'messages',
        'project_files', 'milestones', 'tasks', 'projects', 'match_scores',
        'team_members', 'teams', 'challenge_tags', 'challenges',
        'faculty_profiles', 'business_profiles', 'student_profiles', 'users',
    ]:
        op.drop_table(table)
