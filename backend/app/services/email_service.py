import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.config.settings import settings
from app.models.models import User

# In-memory OTP storage (use Redis in production)
otp_storage = {}


def generate_otp(length=6):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using SMTP"""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP credentials not configured. Email not sent.")
        print(f"Would have sent to {to_email}:")
        print(f"Subject: {subject}")
        print(f"Body: {body}")
        return True  # Return True for development
    
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_FROM_EMAIL or settings.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_password_reset_otp(db: Session, email: str) -> dict:
    """Send OTP for password reset"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}
    
    otp = generate_otp()
    expiry = datetime.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
    
    # Store OTP
    otp_storage[email] = {
        "otp": otp,
        "expiry": expiry,
        "user_id": user.id
    }
    
    # Send email
    subject = "Password Reset OTP - CoreInventory"
    body = f"""Hello {user.name},

Your password reset OTP is: {otp}

This OTP is valid for 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
CoreInventory Team"""
    
    if send_email(email, subject, body):
        return {"success": True, "message": "OTP sent to your email"}
    else:
        return {"success": False, "message": "Failed to send OTP"}


def verify_otp(email: str, otp: str) -> dict:
    """Verify OTP"""
    if email not in otp_storage:
        return {"success": False, "message": "OTP not found or expired"}
    
    stored = otp_storage[email]
    
    if datetime.now() > stored["expiry"]:
        del otp_storage[email]
        return {"success": False, "message": "OTP expired"}
    
    if stored["otp"] != otp:
        return {"success": False, "message": "Invalid OTP"}
    
    return {"success": True, "message": "OTP verified", "user_id": stored["user_id"]}


def reset_password(db: Session, email: str, otp: str, new_password: str) -> dict:
    """Reset password with OTP verification"""
    # Verify OTP first
    verification = verify_otp(email, otp)
    if not verification["success"]:
        return verification
    
    # Update password
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}
    
    from app.services.auth_service import get_password_hash
    user.password = get_password_hash(new_password)
    db.commit()
    
    # Clear OTP
    if email in otp_storage:
        del otp_storage[email]
    
    return {"success": True, "message": "Password reset successful"}
