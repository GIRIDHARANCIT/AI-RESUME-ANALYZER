"""Authentication routes: send OTP, verify OTP, session management."""
import secrets
from typing import Optional
import hashlib

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from services.smtp_auth import send_otp
from services.storage_service import (
    get_user_by_email,
    get_user_by_session,
    save_user,
    update_user_session,
    verify_otp,
)

router = APIRouter()


class SendOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginPasswordRequest(BaseModel):
    email: EmailStr
    password: str


class CheckUserRequest(BaseModel):
    email: EmailStr


class SetPasswordOtpRequest(BaseModel):
    email: EmailStr
    password: str


class SessionResponse(BaseModel):
    session_id: str
    email: str
    role: str


def _hash_password(password: str) -> str:
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, hash_value: str) -> bool:
    """Verify password against hash."""
    return _hash_password(password) == hash_value


@router.post("/check-user")
def api_check_user(req: CheckUserRequest):
    """Check if user exists."""
    user = get_user_by_email(req.email)
    return {"exists": user is not None}


@router.post("/send-otp")
def api_send_otp(req: SendOtpRequest):
    """Send OTP to user email via SMTP."""
    try:
        send_otp(req.email)
        return {"message": "OTP sent successfully", "email": req.email}
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login-password")
def api_login_password(req: LoginPasswordRequest):
    """Login with email and password. New users need OTP verification."""
    user = get_user_by_email(req.email)
    
    if user:
        # Existing user - verify password
        if not _verify_password(req.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # User exists and password is correct - direct login
        session_id = secrets.token_urlsafe(32)
        update_user_session(req.email, session_id)
        return {
            "session_id": session_id,
            "email": req.email,
            "requires_otp": False,
            "message": "Logged in successfully",
        }
    else:
        # New user - create temp session, require OTP for verification
        temp_session = secrets.token_urlsafe(32)
        # Store password temporarily (to be confirmed after OTP)
        save_user(
            req.email,
            {
                "email": req.email,
                "password_hash": _hash_password(req.password),
                "temp_session": temp_session,
                "verified": False,
                "role": "individual",
            },
        )
        # Send OTP for new user registration
        try:
            send_otp(req.email)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")
        
        return {
            "temp_session": temp_session,
            "email": req.email,
            "requires_otp": True,
            "message": "OTP sent for verification",
        }


@router.post("/verify-otp")
def api_verify_otp(req: VerifyOtpRequest):
    """Verify OTP and create session."""
    if not verify_otp(req.email, req.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    session_id = secrets.token_urlsafe(32)
    user = get_user_by_email(req.email)
    
    if user:
        # Update existing user
        update_user_session(req.email, session_id)
    else:
        # Create new user
        save_user(
            req.email,
            {
                "email": req.email,
                "session_id": session_id,
                "verified": True,
                "role": "individual",
            },
        )

    return {
        "session_id": session_id,
        "email": req.email,
        "message": "Verified successfully",
    }


@router.post("/set-password-otp")
def api_set_password_otp(req: SetPasswordOtpRequest):
    """Set password after OTP verification (for new users)."""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Update password for new user
    user["password_hash"] = _hash_password(req.password)
    user["verified"] = True
    save_user(req.email, user)
    
    session_id = secrets.token_urlsafe(32)
    update_user_session(req.email, session_id)
    
    return {
        "session_id": session_id,
        "email": req.email,
        "message": "Password set successfully",
    }


@router.post("/reset-password-otp")
def api_reset_password_otp(req: SetPasswordOtpRequest):
    """Reset password after OTP verification."""
    user = get_user_by_email(req.email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Update password for password reset
    user["password_hash"] = _hash_password(req.password)
    save_user(req.email, user)
    
    session_id = secrets.token_urlsafe(32)
    update_user_session(req.email, session_id)
    
    return {
        "session_id": session_id,
        "email": req.email,
        "message": "Password reset successfully",
    }


def get_current_user(session_id: Optional[str]) -> Optional[dict]:
    """Validate session and return user."""
    if not session_id:
        return None
    return get_user_by_session(session_id)
