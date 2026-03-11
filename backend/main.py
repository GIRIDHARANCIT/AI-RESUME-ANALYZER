"""
ATS Resume Analyzer - FastAPI Backend
Production-ready backend with CORS, file handling, and structured storage.
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from routes import auth, resume, hr, individual, report

# Ensure storage directory exists BEFORE database init
STORAGE_PATH = Path(__file__).parent / "storage"
STORAGE_PATH.mkdir(exist_ok=True)

# Initialize database
try:
    from database import init_db
    init_db()
except Exception as e:
    print(f"[WARNING] Database initialization warning: {e}")
    print("[INFO] App will continue - database will initialize on first request")

app = FastAPI(
    title="ATS Resume Analyzer API",
    description="Production-ready ATS analysis with HR and Individual modes",
    version="1.0.0",
)

# Get CORS origins from environment or use defaults
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api", tags=["Resume"])
app.include_router(hr.router, prefix="/api/hr", tags=["HR Mode"])
app.include_router(individual.router, prefix="/api/individual", tags=["Individual Mode"])
app.include_router(report.router, prefix="/api", tags=["Reports"])

# Mount uploads for report downloads
UPLOADS_PATH = Path(__file__).parent / "uploads"
UPLOADS_PATH.mkdir(exist_ok=True)

REPORTS_PATH = Path(__file__).parent / "storage" / "reports"
REPORTS_PATH.mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """Initialize database on app startup"""
    try:
        from database import init_db
        init_db()
        print("[INFO] Database initialized successfully on startup")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()


@app.get("/")
def root():
    return {"message": "ATS Resume Analyzer API", "status": "running"}


@app.get("/api/health")
def health():
    return {"status": "healthy"}
