"""Application configuration with environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = BASE_DIR / "uploads"

# Ensure directories exist
STORAGE_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# File paths
USERS_DAT = STORAGE_DIR / "users.dat"
REPORTS_DAT = STORAGE_DIR / "reports.dat"

# API Keys (from environment)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))

# File upload limits (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024
# All file types accepted
ALLOWED_EXTENSIONS = None  # None means all extensions allowed
