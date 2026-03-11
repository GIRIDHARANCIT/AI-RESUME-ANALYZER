"""Report download routes."""
import json
from typing import Any, Dict, List

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import STORAGE_DIR
from services.pdf_report import generate_hr_ranking_report
from services.storage_service import get_report, save_report

router = APIRouter()
REPORTS_DIR = STORAGE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class DownloadReportRequest(BaseModel):
    job_description: str
    job_summary: str
    candidates: Any


def _coerce_candidates(raw: Any) -> List[Dict]:
    """
    Accept candidates as:
    - list[dict] (expected)
    - JSON string of list[dict]
    - list[str] where each str is a JSON object
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return _coerce_candidates(parsed)
        except Exception:
            return []
    if isinstance(raw, list):
        out: List[Dict] = []
        for item in raw:
            if isinstance(item, dict):
                out.append(item)
            elif isinstance(item, str):
                try:
                    obj = json.loads(item)
                    if isinstance(obj, dict):
                        out.append(obj)
                except Exception:
                    continue
        return out
    if isinstance(raw, dict):
        return [raw]
    return []


@router.post("/generate-report")
def generate_report(req: DownloadReportRequest):
    """Generate PDF report and return report_id for download."""
    candidates = _coerce_candidates(req.candidates)
    if not candidates:
        raise HTTPException(status_code=400, detail="Invalid candidates payload. Expected a list of candidate objects.")

    report_id = str(uuid4())
    output_path = REPORTS_DIR / f"{report_id}.pdf"
    generate_hr_ranking_report(
        job_description=req.job_description,
        job_summary=req.job_summary or req.job_description[:500],
        candidates=candidates,
        output_path=output_path,
    )
    save_report(report_id, {"path": str(output_path), "candidates": candidates})
    return {"report_id": report_id, "message": "Report generated"}


@router.get("/download-report/{report_id}")
def download_report(report_id: str):
    """Download generated PDF report by ID."""
    report_data = get_report(report_id)
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")

    path = Path(report_data.get("path", ""))
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"ATS_Ranking_Report_{report_id[:8]}.pdf",
    )
