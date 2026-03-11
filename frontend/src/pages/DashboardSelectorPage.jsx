import { useNavigate } from 'react-router-dom'
import { TopNav } from '../components/TopNav'

export function DashboardSelectorPage() {
  const navigate = useNavigate()

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))' }}>
          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>HR Mode</h3>
            <p className="muted">
              Upload multiple resumes, add job description + required skills, analyze, rank, filter, and export PDF report.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/hr')}>
              Open HR Dashboard
            </button>
          </div>
          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Individual User Mode</h3>
            <p className="muted">
              Upload your resume, add target role/company or run general ATS evaluation, get Gemini suggestions and optimize.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/individual')}>
              Open Individual Dashboard
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

