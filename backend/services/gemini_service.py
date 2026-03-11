"""Google Gemini API integration for resume analysis and optimization."""
import json
import os
import re
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def _get_client():
    """Lazy import and init of Gemini."""
    print(f"[DEBUG] GEMINI_API_KEY loaded: {bool(GEMINI_API_KEY)}")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment")
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Use the latest available models
    model_name = "gemini-2.5-flash"  # Latest, fastest, most cost-effective
    print(f"[DEBUG] Using model: {model_name}")
    return genai.GenerativeModel(model_name)


def _fallback_analysis(resume_text: str) -> Dict[str, Any]:
    """
    Safe fallback when Gemini is unavailable: returns a minimal structured response
    so the endpoint doesn't 500 during local setup.
    """
    text = resume_text.lower()
    missing = []
    for kw in ["impact", "metrics", "leadership", "ownership", "api", "sql", "python", "react", "docker", "aws"]:
        if kw not in text:
            missing.append(kw)
    return {
        "strengths": ["Basic ATS scoring computed successfully (Gemini unavailable)."],
        "weaknesses": ["Gemini AI analysis is not configured or temporarily unavailable."],
        "missing_keywords": missing[:10],
        "improvement_suggestions": [
            "Add quantified achievements (numbers, %, time saved, revenue impact).",
            "Tailor keywords to the target job description and required skills.",
            "Rewrite bullets using action verbs + outcomes.",
        ],
        "summary_rewrite": "",
        "bullet_rewrites": [],
        "overall_score_explanation": "Set GEMINI_API_KEY in backend/.env to enable AI suggestions.",
    }


def analyze_resume_individual(
    resume_text: str,
    target_position: Optional[str] = None,
    company_name: Optional[str] = None,
    job_description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze resume for individual user: strengths, weaknesses, missing keywords,
    improvement suggestions, summary rewrite, bullet point rewrites.
    """
    try:
        model = _get_client()
    except Exception as e:
        print(f"[ERROR] Failed to initialize Gemini client: {e}")
        import traceback
        traceback.print_exc()
        return _fallback_analysis(resume_text)
    context = []
    if target_position:
        context.append(f"Target position: {target_position}")
    if company_name:
        context.append(f"Company: {company_name}")
    if job_description:
        context.append(f"Job description:\n{job_description[:2000]}")

    prompt = f"""You are an expert ATS resume analyst and career coach.

Analyze the following resume and provide structured feedback.

Resume text:
---
{resume_text[:8000]}
---

{f"Additional context: {'; '.join(context)}" if context else ""}

Respond in valid JSON only, with this exact structure (no markdown, no code blocks):
{{
  "strengths": ["strength1", "strength2", "strength3"],
  "weaknesses": ["weakness1", "weakness2"],
  "missing_keywords": ["keyword1", "keyword2", "keyword3"],
  "improvement_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
  "summary_rewrite": "Improved professional summary paragraph (2-4 sentences)",
  "bullet_rewrites": [
    {{"original": "original bullet text", "improved": "improved bullet with impact and metrics"}},
    {{"original": "another bullet", "improved": "improved version"}}
  ],
  "overall_score_explanation": "Brief explanation of resume strength (1-2 sentences)"
}}

Provide 2-4 bullet rewrites for the most impactful experience bullets. Be specific and actionable."""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code blocks if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON decode error: {e}")
        return {
            "strengths": ["Unable to parse AI response"],
            "weaknesses": [],
            "missing_keywords": [],
            "improvement_suggestions": ["Please try again or provide more resume content"],
            "summary_rewrite": "",
            "bullet_rewrites": [],
            "overall_score_explanation": str(e),
        }
    except Exception as e:
        print(f"[ERROR] Gemini API error during generate_content: {e}")
        import traceback
        traceback.print_exc()
        return _fallback_analysis(resume_text)


def optimize_resume(
    resume_text: str,
    suggestions: Dict[str, Any],
    user_edits: Optional[Dict[str, str]] = None,
) -> str:
    """
    Generate optimized resume text incorporating suggestions and optional user edits.
    """
    try: 
        print("Gemini client initialized successfully in optimize_resume.")
        model = _get_client()
    except Exception as e:
        raise RuntimeError("Gemini is not configured. Set GEMINI_API_KEY in backend/.env") from e
    edits_str = ""
    if user_edits:
        edits_str = f"\nUser-specified edits to apply:\n{json.dumps(user_edits, indent=2)}"

    prompt = f"""You are an expert resume writer. Generate an improved, ATS-optimized version of this resume.

Original resume:
---
{resume_text[:8000]}
---

Analysis and suggestions to incorporate:
{json.dumps(suggestions, indent=2)}
{edits_str}

Output the COMPLETE improved resume as plain text. Preserve the structure (sections, headings) but improve:
- Summary section
- Bullet points (use strong action verbs, quantify achievements)
- Keyword alignment
- Clarity and impact

Do not add any preamble or explanation. Output only the resume text."""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {str(e)}")
def extract_applicant_name(resume_text: str) -> str:
    """
    Extract applicant name from resume using Gemini API.
    Falls back to heuristic if API fails.
    """
    try:
        model = _get_client()
    except Exception as e:
        print(f"[DEBUG] Gemini not available for name extraction: {e}")
        return None  # Return None to fall back to heuristic
    
    prompt = f"""Extract ONLY the applicant's full name from this resume. 

Resume:
---
{resume_text[:2000]}
---

Respond with ONLY the name in this JSON format (nothing else):
{{"name": "Full Name"}}

If you cannot determine a clear name, respond with:
{{"name": null}}
"""
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Remove markdown code blocks if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        result = json.loads(text)
        name = result.get("name")
        if name and isinstance(name, str) and len(name.strip()) > 0:
            return name.strip()
        return None
    except Exception as e:
        print(f"[DEBUG] Failed to extract name via Gemini: {e}")
        return None


print(f"GEMINI_API_KEY in gemini_service.py: {GEMINI_API_KEY}")