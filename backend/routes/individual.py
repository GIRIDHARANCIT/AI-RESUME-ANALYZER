"""Individual User Mode: single resume analysis and optimization."""
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import STORAGE_DIR
from services.ats_engine import compute_ats_score
from services.gemini_service import analyze_resume_individual, optimize_resume
from services.resume_formats import text_to_pdf, text_to_docx, text_to_txt

router = APIRouter()
OPTIMIZED_DIR = STORAGE_DIR / "optimized"
OPTIMIZED_DIR.mkdir(parents=True, exist_ok=True)


class AnalyzeResumeRequest(BaseModel):
    resume_text: str
    target_position: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    general_ats: bool = False


class OptimizeResumeRequest(BaseModel):
    resume_text: str
    suggestions: Dict[str, Any]
    user_edits: Optional[Dict[str, str]] = None


@router.post("/analyze-resume")
def analyze_resume(req: AnalyzeResumeRequest):
    """
    Analyze single resume using Gemini: strengths, weaknesses, missing keywords,
    improvement suggestions, bullet rewrites, summary rewrite.
    """
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required")

    # ATS score (use job description if provided, else generic)
    job_desc = req.job_description or "Software engineer with strong technical skills."
    skills = []
    if req.job_description:
        # Extract some skills from job description heuristically
        words = job_desc.lower().split()
        tech_terms = ["python", "java", "javascript", "react", "sql", "aws", "docker", "api", "machine learning"]
        skills = [t for t in tech_terms if t in job_desc.lower()]

    ats_result = compute_ats_score(
        resume_text=req.resume_text,
        job_description=job_desc,
        required_skills=skills,
    )

    try:
        gemini_result = analyze_resume_individual(
            resume_text=req.resume_text,
            target_position=req.target_position,
            company_name=req.company_name,
            job_description=req.job_description if not req.general_ats else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "ats_score": ats_result["ats_score"],
        "breakdown": ats_result["breakdown"],
        "strengths": gemini_result.get("strengths", []),
        "weaknesses": gemini_result.get("weaknesses", []),
        "missing_skills": gemini_result.get("missing_keywords", []),
        "improvement_suggestions": gemini_result.get("improvement_suggestions", []),
        "summary_rewrite": gemini_result.get("summary_rewrite", ""),
        "bullet_rewrites": gemini_result.get("bullet_rewrites", []),
        "overall_score_explanation": gemini_result.get("overall_score_explanation", ""),
        "suggestions_raw": gemini_result,
    }


@router.post("/optimize-resume")
def api_optimize_resume(req: OptimizeResumeRequest):
    """Generate optimized resume from original + suggestions + optional user edits."""
    if not req.resume_text.strip():
        raise HTTPException(status_code=400, detail="Resume text is required")

    try:
        optimized = optimize_resume(
            resume_text=req.resume_text,
            suggestions=req.suggestions,
            user_edits=req.user_edits,
        )
        return {"optimized_text": optimized}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


class DownloadOptimizedRequest(BaseModel):
    optimized_text: str


@router.post("/download-optimized-pdf")
def download_optimized_pdf(req: DownloadOptimizedRequest):
    """Convert optimized resume text to PDF and return file."""
    if not req.optimized_text.strip():
        raise HTTPException(status_code=400, detail="Optimized text is required")

    file_id = str(uuid4())
    output_path = OPTIMIZED_DIR / f"{file_id}.pdf"
    text_to_pdf(req.optimized_text, output_path)
    return FileResponse(
        output_path,
        media_type="application/pdf",
        filename="Optimized_Resume.pdf",
    )


@router.post("/download-optimized-docx")
def download_optimized_docx(req: DownloadOptimizedRequest):
    """Convert optimized resume text to DOCX and return file."""
    if not req.optimized_text.strip():
        raise HTTPException(status_code=400, detail="Optimized text is required")

    file_id = str(uuid4())
    output_path = OPTIMIZED_DIR / f"{file_id}.docx"
    text_to_docx(req.optimized_text, output_path)
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="Optimized_Resume.docx",
    )


@router.post("/download-optimized-txt")
def download_optimized_txt(req: DownloadOptimizedRequest):
    """Save optimized resume text as TXT and return file."""
    if not req.optimized_text.strip():
        raise HTTPException(status_code=400, detail="Optimized text is required")

    file_id = str(uuid4())
    output_path = OPTIMIZED_DIR / f"{file_id}.txt"
    text_to_txt(req.optimized_text, output_path)
    return FileResponse(
        output_path,
        media_type="text/plain",
        filename="Optimized_Resume.txt",
    )
