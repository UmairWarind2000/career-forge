from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.deps import get_current_user
from core.security import hash_password, verify_password
from models.user import User
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/profile", tags=["User Profile"])

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    target_role: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

@router.get("/me")
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "target_role": current_user.target_role,
        "readiness_score": current_user.readiness_score,
        "bio": getattr(current_user, 'bio', None),
        "location": getattr(current_user, 'location', None),
        "linkedin_url": getattr(current_user, 'linkedin_url', None),
        "github_url": getattr(current_user, 'github_url', None),
        "portfolio_url": getattr(current_user, 'portfolio_url', None),
        "member_since": current_user.created_at.strftime("%B %Y") if current_user.created_at else None,
        "avatar_letter": current_user.full_name[0].upper() if current_user.full_name else "U",
    }

@router.put("/update")
def update_profile(
    data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data provided")

    db.query(User).filter(User.id == current_user.id).update(update_data)
    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully",
        "user": {
            "full_name": current_user.full_name,
            "target_role": current_user.target_role,
        }
    }

@router.put("/change-password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    db.query(User).filter(User.id == current_user.id).update({
        "hashed_password": hash_password(data.new_password)
    })
    db.commit()

    return {"message": "Password changed successfully"}