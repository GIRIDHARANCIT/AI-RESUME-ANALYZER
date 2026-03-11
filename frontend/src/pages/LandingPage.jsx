import { Link } from 'react-router-dom'

export function LandingPage() {
  return (
    <div className="container">
      <div className="card" style={{ padding: 28 }}>
        <div style={{ maxWidth: 760, margin: '0 auto' }}>
          <h1 style={{ margin: 0, fontSize: 36, textAlign: 'center' }}>ATS Resume Analyzer</h1>
          <p className="muted" style={{ marginTop: 10, fontSize: 16, textAlign: 'center' }}>
            Production-ready web app with HR batch ranking, Individual AI feedback, OTP email login, PDF/DOCX parsing,
            TF‑IDF + cosine similarity ATS scoring, and downloadable PDF reports.
          </p>
          <div
            className="row"
            style={{
              marginTop: 18,
              justifyContent: 'center',
              gap: 12,
              flexWrap: 'wrap',
            }}
          >
            <Link className="btn btn-primary" to="/login" style={{ minWidth: 160 }}>
              Login with Gmail
            </Link>
            <Link className="btn btn-ghost" to="/select-mode" style={{ minWidth: 160 }}>
              Go to Dashboard
            </Link>
          </div>
          <div className="grid" style={{ marginTop: 22, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ fontWeight: 700 }}>HR Mode</div>
              <div className="muted" style={{ marginTop: 6 }}>
                Upload multiple resumes, add job description + skills, get ranked list, filters, search, and PDF report.
              </div>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ fontWeight: 700 }}>Individual Mode</div>
              <div className="muted" style={{ marginTop: 6 }}>
                Gemini feedback: strengths/weaknesses, missing keywords, bullet rewrites, better summary, optimize + PDF.
              </div>
            </div>
            <div className="card" style={{ padding: 16 }}>
              <div style={{ fontWeight: 700 }}>ATS Scoring</div>
              <div className="muted" style={{ marginTop: 6 }}>
                40% keyword match, 30% skills match, 20% experience relevance, 10% formatting & structure.
              </div>
            </div>
          </div>
          <p className="muted" style={{ marginTop: 18, textAlign: 'center' }}>
            Backend: FastAPI · Storage: SQLite DB · AI: Google Gemini · Auth: Gmail + Password + OTP
          </p>
        </div>
      </div>
    </div>
  )
}

