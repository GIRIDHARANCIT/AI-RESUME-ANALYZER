"""Storage service - uses SQLite database instead of .dat files."""
from typing import Dict, Optional

from database import (
    get_user_by_email as db_get_user_by_email,
    save_user as db_save_user,
    update_user_session as db_update_user_session,
    get_user_by_session as db_get_user_by_session,
    store_otp as db_store_otp,
    verify_otp as db_verify_otp,
    save_report as db_save_report,
    get_report as db_get_report,
)


# User storage - now uses database
def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email from database."""
    return db_get_user_by_email(email)


def save_user(email: str, user_data: Dict) -> None:
    """Save or update user in database."""
    db_save_user(email, user_data)


def update_user_session(email: str, session_id: str) -> None:
    """Update user session after OTP verification."""
    db_update_user_session(email, session_id)


def get_user_by_session(session_id: str) -> Optional[Dict]:
    """Get user by session ID from database."""
    return db_get_user_by_session(session_id)


# OTP storage - now uses database
def store_otp(email: str, otp: str, expiry_timestamp: float) -> None:
    """Store OTP with expiry in database."""
    db_store_otp(email, otp, expiry_timestamp)


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP and remove if valid from database."""
    return db_verify_otp(email, otp)


# Report storage - now uses database
def save_report(report_id: str, report_data: Dict) -> None:
    """Save report metadata to database."""
    db_save_report(report_id, report_data)


def get_report(report_id: str) -> Optional[Dict]:
    """Get report by ID from database."""
    return db_get_report(report_id)
