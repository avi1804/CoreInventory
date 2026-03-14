from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import UserCreate, UserLogin, LoginResponse, UserResponse, MessageResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=MessageResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        auth_service.signup(db, user)
        return MessageResponse(message="User Registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth_service.login(db, user)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found or wrong password")
    return LoginResponse(message="Login success", user=db_user)
