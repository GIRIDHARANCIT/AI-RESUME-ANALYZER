import json
import sys
import time

import requests


BASE = "http://127.0.0.1:8000"


def _req(method: str, path: str, **kwargs):
    r = requests.request(method, BASE + path, timeout=30, **kwargs)
    return r.status_code, r.headers, r.text, r.content


def main() -> int:
    # Health (wait for server up)
    last = None
    for _ in range(20):
        try:
            code, _, text, _ = _req("GET", "/api/health")
            last = (code, text)
            if code == 200:
                break
        except Exception as e:
            last = (None, str(e))
            time.sleep(0.5)
    if not last:
        return 2
    print("health", last[0], last[1])
    if last[0] != 200:
        return 2

    # OTP verify wrong
    code, _, text, _ = _req("POST", "/api/auth/verify-otp", json={"email": "test@example.com", "otp": "000000"})
    print("verify-otp(wrong)", code)
    if code not in (400, 422):
        print(text)
        return 3

    # Individual analyze (Gemini may fallback)
    payload = {
        "resume_text": "John Doe\nSkills: Python, FastAPI, React\nExperience: Built APIs and dashboards.",
        "target_position": "Full Stack Developer",
        "company_name": "Acme",
        "job_description": None,
        "general_ats": True,
    }
    code, _, text, _ = _req("POST", "/api/individual/analyze-resume", json=payload)
    print("individual analyze", code)
    if code != 200:
        print(text)
        return 4
    obj = json.loads(text)
    assert isinstance(obj.get("ats_score"), (int, float))

    # HR batch analyze
    hr_payload = {
        "resumes": [
            {
                "file_id": "1",
                "filename": "a.pdf",
                "extracted_text": "Alice\nSkills: Python React\nExperience: 3 years\n- Built APIs",
                "candidate_name": "Alice",
            },
            {
                "file_id": "2",
                "filename": "b.pdf",
                "extracted_text": "Bob\nSkills: Java SQL\nExperience: 5 years\n- Led team",
                "candidate_name": "Bob",
            },
        ],
        "job_description": "We need Python React developer with API experience",
        "required_skills": ["Python", "React", "API"],
    }
    code, _, text, _ = _req("POST", "/api/hr/analyze-batch", json=hr_payload)
    print("hr analyze batch", code)
    if code != 200:
        print(text)
        return 5
    data = json.loads(text)
    assert "candidates" in data and isinstance(data["candidates"], list)

    # Generate + download report
    rep_payload = {
        "job_description": data["job_description"],
        "job_summary": data["job_description"][:200],
        "candidates": data["candidates"],
    }
    code, _, text, _ = _req("POST", "/api/generate-report", json=rep_payload)
    print("generate report", code)
    if code != 200:
        print(text)
        return 6
    rid = json.loads(text)["report_id"]
    code, headers, _, content = _req("GET", f"/api/download-report/{rid}")
    print("download report", code, headers.get("content-type"))
    if code != 200 or not content:
        return 7

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

