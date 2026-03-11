## ATS Resume Analyzer (HR + Individual)

### Tech stack
- **Frontend**: React (Vite)
- **Backend**: Python FastAPI
- **AI**: Google Gemini low-cost model (`gemini-1.5-flash`)
- **Auth**: Gmail OTP via SMTP
- **Storage**: structured `.dat` files (no database)
- **Resumes**: PDF / DOCX parsing + ATS scoring (TF‑IDF + cosine similarity)

---

### Folder structure
- `frontend/` React app
- `backend/` FastAPI app
- `backend/storage/` `.dat` + generated PDFs

---

### Backend setup (Windows PowerShell)
From `project-root/backend`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:
- `GEMINI_API_KEY=...`
- `SMTP_USER=your_gmail@gmail.com`
- `SMTP_PASSWORD=your_gmail_app_password`

Run API:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

### Frontend setup
From `project-root/frontend`:

```bash
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`.

If you need to change backend URL, create `frontend/.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

### Implemented API endpoints (base: `/api`)
- `POST /auth/send-otp`
- `POST /auth/verify-otp`
- `POST /upload-resume`
- `POST /individual/analyze-resume`
- `POST /individual/optimize-resume`
- `POST /individual/download-optimized-pdf`
- `POST /hr/analyze-batch`
- `POST /generate-report`
- `GET /download-report/{report_id}`

