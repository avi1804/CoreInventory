from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import UserProfileUpdate, UserProfileResponse, MessageResponse
from app.services import auth_service
from app.models.models import User

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(user_id: int, db: Session = Depends(get_db)):
    """Get current user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/update", response_model=MessageResponse)
def update_profile(user_id: int, profile: UserProfileUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if profile.name:
        user.name = profile.name
    if profile.email:
        # Check if email already exists
        existing = db.query(User).filter(User.email == profile.email).first()
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        user.email = profile.email
    
    db.commit()
    db.refresh(user)
    return MessageResponse(message="Profile Updated")


@router.post("/logout", response_model=MessageResponse)
def logout():
    """Logout user (client-side token removal)"""
    return MessageResponse(message="Logged out successfully")
