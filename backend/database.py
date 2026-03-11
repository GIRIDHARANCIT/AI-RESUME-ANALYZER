"""SQLite database setup and connection management."""
import json
from pathlib import Path
from typing import Optional, Dict, Any

from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm Script start.sh not found
✖ 
No start command was found

. import sessionmaker, Session
import datetime

# Database setup
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "storage" / "ats_analyzer.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create tables
Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    email = Column(String(255), primary_key=True, index=True)
    password_hash = Column(String(255))
    session_id = Column(String(255), unique=True, nullable=True, index=True)
    verified = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class Report(Base):
    """Report model for storing report metadata."""
    __tablename__ = "reports"
    
    report_id = Column(String(255), primary_key=True, index=True)
    path = Column(String(1024))
    candidates = Column(JSON)  # Store candidates as JSON
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class OTPStore(Base):
    """OTP storage model."""
    __tablename__ = "otp_store"
    
    email = Column(String(255), primary_key=True, index=True)
    otp = Column(String(10))
    expiry = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# Create engine
def get_engine():
    """Get SQLAlchemy engine with SQLite."""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        # Test connection
        with engine.connect() as conn:
            pass
        print(f"[Database] Engine created successfully at {DB_PATH}")
        return engine
    except Exception as e:
        print(f"[ERROR] Failed to create database engine: {e}")
        raise


# Create session factory
try:
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    print(f"[ERROR] Failed to initialize database session: {e}")
    raise


def init_db():
    """Initialize database tables with error handling."""
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        Base.metadata.create_all(bind=engine)
        print(f"[Database] Initialized SQLite at {DB_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# User operations
def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if user:
            return {
                "email": user.email,
                "password_hash": user.password_hash,
                "session_id": user.session_id,
                "verified": bool(user.verified),
            }
        return None
    finally:
        db.close()


def save_user(email: str, user_data: Dict) -> None:
    """Save or update user."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if user:
            # Update
            user.password_hash = user_data.get("password_hash", user.password_hash)
            user.session_id = user_data.get("session_id", user.session_id)
            user.verified = user_data.get("verified", user.verified)
        else:
            # Create
            user = User(
                email=email.lower(),
                password_hash=user_data.get("password_hash", ""),
                session_id=user_data.get("session_id"),
                verified=user_data.get("verified", 0),
            )
            db.add(user)
        db.commit()
    finally:
        db.close()


def update_user_session(email: str, session_id: str) -> None:
    """Update user session."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.lower()).first()
        if user:
            user.session_id = session_id
            user.verified = 1
            db.commit()
    finally:
        db.close()


def get_user_by_session(session_id: str) -> Optional[Dict]:
    """Get user by session ID."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.session_id == session_id).first()
        if user:
            return {
                "email": user.email,
                "password_hash": user.password_hash,
                "session_id": user.session_id,
                "verified": bool(user.verified),
            }
        return None
    finally:
        db.close()


# OTP operations
def store_otp(email: str, otp: str, expiry_timestamp: float) -> None:
    """Store OTP with expiry."""
    db = SessionLocal()
    try:
        otp_record = db.query(OTPStore).filter(OTPStore.email == email.lower()).first()
        expiry = datetime.datetime.fromtimestamp(expiry_timestamp)
        if otp_record:
            otp_record.otp = otp
            otp_record.expiry = expiry
        else:
            otp_record = OTPStore(
                email=email.lower(),
                otp=otp,
                expiry=expiry,
            )
            db.add(otp_record)
        db.commit()
    finally:
        db.close()


def verify_otp(email: str, otp: str) -> bool:
    """Verify OTP and remove if valid."""
    db = SessionLocal()
    try:
        otp_record = db.query(OTPStore).filter(OTPStore.email == email.lower()).first()
        if not otp_record:
            return False
        
        if datetime.datetime.utcnow() > otp_record.expiry:
            db.delete(otp_record)
            db.commit()
            return False
        
        if otp_record.otp == otp:
            db.delete(otp_record)
            db.commit()
            return True
        
        return False
    finally:
        db.close()


# Report operations
def save_report(report_id: str, report_data: Dict) -> None:
    """Save report metadata."""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.report_id == report_id).first()
        if report:
            report.path = report_data.get("path")
            report.candidates = report_data.get("candidates")
        else:
            report = Report(
                report_id=report_id,
                path=report_data.get("path"),
                candidates=report_data.get("candidates"),
            )
            db.add(report)
        db.commit()
    finally:
        db.close()


def get_report(report_id: str) -> Optional[Dict]:
    """Get report by ID."""
    db = SessionLocal()
    try:
        report = db.query(Report).filter(Report.report_id == report_id).first()
        if report:
            return {
                "path": report.path,
                "candidates": report.candidates,
            }
        return None
    finally:
        db.close()
