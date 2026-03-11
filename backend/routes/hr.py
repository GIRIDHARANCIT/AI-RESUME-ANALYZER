"""HR Mode: batch resume analysis."""
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ats_engine import compute_ats_score
from services.resume_parser import extract_name_from_resume, extract_text

router = APIRouter()


class ResumeInput(BaseModel):
    file_id: str
    filename: str
    extracted_text: str
    candidate_name: str
    applicant_name: str = None  # Optional: applicant name provided by HR


class HrAnalyzeRequest(BaseModel):
    resumes: List[ResumeInput]
    job_description: str
    required_skills: List[str]


@router.post("/analyze-batch")
def hr_analyze_batch(req: HrAnalyzeRequest):
    """
    Analyze multiple resumes against job description and skills.
    Returns ranked list by ATS score (descending).
    """
    if not req.resumes:
        raise HTTPException(status_code=400, detail="No resumes provided")

    results = []
    for r in req.resumes:
        text = r.extracted_text or ""
        name = r.candidate_name or extract_name_from_resume(text)
        # Use applicant_name if provided, otherwise use candidate_name
        display_name = r.applicant_name if r.applicant_name else name
        score_data = compute_ats_score(
            resume_text=text,
            job_description=req.job_description,
            required_skills=req.required_skills,
        )
        results.append({
            "file_id": r.file_id,
            "filename": r.filename,
            "candidate_name": name,
            "applicant_name": display_name,
            "ats_score": score_data["ats_score"],
            "skills_match_pct": score_data["skills_match_pct"],
            "keyword_match_pct": score_data["keyword_match_pct"],
            "missing_skills": score_data["missing_skills"],
            "breakdown": score_data["breakdown"],
        })

    # Sort by ATS score descending
    results.sort(key=lambda x: x["ats_score"], reverse=True)

    return {
        "candidates": results,
        "job_description": req.job_description,
        "required_skills": req.required_skills,
    }
