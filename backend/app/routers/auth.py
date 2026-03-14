from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import UserCreate, UserLogin, LoginResponse, UserResponse, MessageResponse, OTPRequest, OTPVerify, PasswordReset
from app.services import auth_service, email_service

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
    result = auth_service.login(db, user)
    if not result:
        raise HTTPException(status_code=400, detail="User not found or wrong password")
    return LoginResponse(
        message="Login success",
        user=result["user"],
        access_token=result["access_token"],
        token_type=result["token_type"]
    )


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(request: OTPRequest, db: Session = Depends(get_db)):
    """Request password reset OTP"""
    result = email_service.send_password_reset_otp(db, request.email)
    if result["success"]:
        return MessageResponse(message=result["message"])
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.post("/verify-otp", response_model=MessageResponse)
def verify_otp(verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP code"""
    result = email_service.verify_otp(db, verify.email, verify.otp)
    if result["success"]:
        return MessageResponse(message=result["message"])
    else:
        raise HTTPException(status_code=400, detail=result["message"])


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(reset: PasswordReset, db: Session = Depends(get_db)):
    """Reset password with OTP"""
    result = email_service.reset_password(db, reset.email, reset.otp, reset.new_password)
    if result["success"]:
        return MessageResponse(message=result["message"])
    else:
        raise HTTPException(status_code=400, detail=result["message"])
