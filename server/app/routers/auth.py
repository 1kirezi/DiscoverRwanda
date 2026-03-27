from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole, VerificationStatus, StudentProfile, BusinessProfile, FacultyProfile
from app.schemas.user import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, get_current_active_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    verification = (
        VerificationStatus.PENDING
        if payload.role == UserRole.BUSINESS
        else VerificationStatus.NOT_REQUIRED
    )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
        verification_status=verification,
    )
    db.add(user)
    db.flush()

    # Create role-specific profile
    if payload.role == UserRole.STUDENT:
        db.add(StudentProfile(user_id=user.id))
    elif payload.role == UserRole.BUSINESS:
        db.add(BusinessProfile(user_id=user.id, business_name=payload.full_name))
    elif payload.role == UserRole.FACULTY:
        db.add(FacultyProfile(user_id=user.id))

    db.commit()
    db.refresh(user)

    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.is_active == True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserOut.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if data.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    user = db.query(User).filter(User.id == int(data["sub"]), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user
