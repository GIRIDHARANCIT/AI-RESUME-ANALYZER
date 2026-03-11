"""Resume upload and parsing routes."""
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOADS_DIR
from services.resume_parser import extract_name_from_resume, extract_text

router = APIRouter()


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...), applicant_name: str = None):
    """Upload resume (any file type), validate, save, and return extracted text + metadata."""
    suffix = Path(file.filename or "").suffix.lower()

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    file_id = str(uuid.uuid4())
    save_path = UPLOADS_DIR / f"{file_id}{suffix}"
    try:
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        text = extract_text(save_path)
        extracted_name = extract_name_from_resume(text)
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))

    # Use applicant_name if provided, otherwise use extracted name
    candidate_name = applicant_name if applicant_name else extracted_name

    return {
        "file_id": file_id,
        "filename": file.filename,
        "suffix": suffix,
        "extracted_text": text,
        "candidate_name": extracted_name,  # Extracted from resume
        "applicant_name": candidate_name,  # User-provided or extracted name
    }
