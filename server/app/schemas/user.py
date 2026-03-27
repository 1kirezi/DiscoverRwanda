from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole, VerificationStatus


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserOut"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User ──────────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    verification_status: VerificationStatus
    avatar_url: Optional[str]
    bio: Optional[str]
    preferred_language: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = None


class StudentProfileOut(BaseModel):
    id: int
    academic_program: Optional[str]
    year_of_study: Optional[int]
    skills_inventory: List[str]
    career_interests: List[str]
    availability_hours_per_week: int
    linkedin_url: Optional[str]
    github_url: Optional[str]
    portfolio_summary: Optional[str]
    completed_projects_count: int
    total_badges: int

    class Config:
        from_attributes = True


class StudentProfileUpdate(BaseModel):
    academic_program: Optional[str] = None
    year_of_study: Optional[int] = None
    skills_inventory: Optional[List[str]] = None
    career_interests: Optional[List[str]] = None
    availability_hours_per_week: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_summary: Optional[str] = None


class BusinessProfileOut(BaseModel):
    id: int
    business_name: str
    business_type: Optional[str]
    size: Optional[str]
    country: Optional[str]
    city: Optional[str]
    website: Optional[str]
    technology_needs: List[str]
    partnership_level: str
    subscription_tier: str

    class Config:
        from_attributes = True


class BusinessProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    size: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    website: Optional[str] = None
    technology_needs: Optional[List[str]] = None


class VerificationRequest(BaseModel):
    documents: List[str]   # list of uploaded file URLs
