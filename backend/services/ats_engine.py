"""
ATS Scoring Engine using TF-IDF, cosine similarity, and keyword matching.
Score breakdown: 40% keyword match, 30% skills match, 20% experience relevance, 10% formatting.
"""
import re
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _tokenize(text: str) -> List[str]:
    """Simple tokenization: lowercase, alphanumeric tokens."""
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    return tokens


def _extract_keywords(text: str, top_n: int = 50) -> List[str]:
    """Extract top keywords by frequency (excluding common stop words)."""
    stop = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "this", "that", "these", "those", "it", "its", "i", "me", "my",
        "we", "our", "you", "your", "he", "she", "they", "them"
    }
    tokens = _tokenize(text)
    freq = {}
    for t in tokens:
        if t not in stop and len(t) > 1:
            freq[t] = freq.get(t, 0) + 1
    sorted_items = sorted(freq.items(), key=lambda x: -x[1])
    return [w for w, _ in sorted_items[:top_n]]


def _keyword_match_score(resume_text: str, job_keywords: List[str]) -> float:
    """Percentage of job keywords found in resume (0-100)."""
    if not job_keywords:
        return 100.0
    resume_lower = resume_text.lower()
    found = sum(1 for kw in job_keywords if kw.lower() in resume_lower)
    return (found / len(job_keywords)) * 100


def _skills_match_score(resume_text: str, required_skills: List[str]) -> Tuple[float, List[str]]:
    """Skills match percentage and list of missing skills (using word boundary matching)."""
    if not required_skills:
        return 100.0, []
    
    resume_lower = resume_text.lower()
    missing = []
    
    for skill in required_skills:
        skill_lower = skill.lower().strip()
        if not skill_lower:
            continue
        
        # Use word boundary regex for accurate matching
        # This ensures "java" doesn't match "javascript"
        pattern = r'\b' + re.escape(skill_lower) + r'\b'
        
        if not re.search(pattern, resume_lower):
            missing.append(skill)
    
    matched = len(required_skills) - len(missing)
    score = (matched / len(required_skills)) * 100 if required_skills else 100.0
    return score, missing


def _experience_relevance_score(resume_text: str, job_description: str) -> float:
    """TF-IDF cosine similarity between resume and job description (0-100 scale)."""
    if not resume_text.strip() or not job_description.strip():
        return 50.0
    vectorizer = TfidfVectorizer(max_features=500, stop_words="english")
    try:
        matrix = vectorizer.fit_transform([resume_text, job_description])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(max(0, min(100, float(sim) * 100)))
    except Exception:
        return 50.0


def _formatting_score(text: str) -> float:
    """Heuristic for structure: sections, length, bullet points (0-100)."""
    score = 50.0
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # Reasonable length
    if 20 <= len(lines) <= 80:
        score += 15
    elif 10 <= len(lines) < 20 or 80 < len(lines) <= 120:
        score += 5
    # Bullet points
    bullets = sum(1 for l in lines if l.startswith(("•", "-", "*", "◦")))
    if bullets >= 5:
        score += 20
    elif bullets >= 2:
        score += 10
    # Section headers (common)
    headers = ["experience", "education", "skills", "summary", "objective", "projects"]
    found_headers = sum(1 for h in headers if any(h in l.lower() for l in lines))
    if found_headers >= 3:
        score += 15
    elif found_headers >= 1:
        score += 5
    return min(100, score)


def compute_ats_score(
    resume_text: str,
    job_description: str,
    required_skills: List[str],
) -> dict:
    """
    Compute ATS score with breakdown.
    Weights: 40% keyword, 30% skills, 20% experience relevance, 10% formatting.
    """
    job_keywords = _extract_keywords(job_description, 30)
    keyword_score = _keyword_match_score(resume_text, job_keywords)
    skills_score, missing_skills = _skills_match_score(resume_text, required_skills)
    exp_score = _experience_relevance_score(resume_text, job_description)
    format_score = _formatting_score(resume_text)

    # Ensure pure Python floats for JSON serialization
    keyword_score = float(keyword_score)
    skills_score = float(skills_score)
    exp_score = float(exp_score)
    format_score = float(format_score)

    total = (
        0.40 * keyword_score +
        0.30 * skills_score +
        0.20 * exp_score +
        0.10 * format_score
    )
    total = float(round(min(100, max(0.0, float(total))), 1))

    return {
        "ats_score": total,
        "breakdown": {
            "keyword_match": float(round(keyword_score, 1)),
            "skills_match": float(round(skills_score, 1)),
            "experience_relevance": float(round(exp_score, 1)),
            "formatting_quality": float(round(format_score, 1)),
        },
        "missing_skills": missing_skills,
        "keyword_match_pct": float(round(keyword_score, 1)),
        "skills_match_pct": float(round(skills_score, 1)),
    }
