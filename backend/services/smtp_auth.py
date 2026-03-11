"""SMTP-based OTP email authentication."""
import random
import smtplib
import string
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import OTP_EXPIRY_MINUTES, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

from .storage_service import store_otp


def generate_otp(length: int = 6) -> str:
    """Generate numeric OTP."""
    return "".join(random.choices(string.digits, k=length))


def send_otp_email(to_email: str, otp: str) -> bool:
    """
    Send OTP via SMTP (Gmail).
    Requires: SMTP_USER, SMTP_PASSWORD (use App Password for Gmail).
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        raise ValueError("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "ATS Resume Analyzer - Your OTP"
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>ATS Resume Analyzer - OTP Verification</h2>
        <p>Your one-time password is:</p>
        <h1 style="color: #2563eb; letter-spacing: 8px;">{otp}</h1>
        <p>This OTP expires in {OTP_EXPIRY_MINUTES} minutes.</p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to send OTP email: {str(e)}")


def send_otp(to_email: str) -> str:
    """
    Generate OTP, send via email, store with expiry.
    Returns the OTP (for dev/testing; in production you wouldn't return it).
    """
    otp = generate_otp()
    send_otp_email(to_email, otp)
    expiry = time.time() + (OTP_EXPIRY_MINUTES * 60)
    store_otp(to_email, otp, expiry)
    return otp
