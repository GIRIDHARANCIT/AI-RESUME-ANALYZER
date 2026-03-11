import { Link, useNavigate } from 'react-router-dom'
import { clearSession } from '../services/auth'

export function TopNav() {
  const navigate = useNavigate()
  const email = localStorage.getItem('email')

  return (
    <div className="container">
      <div className="card" style={{ padding: 14 }}>
        <div className="row" style={{ justifyContent: 'space-between' }}>
          <div className="row" style={{ gap: 10 }}>
            <Link to="/" style={{ fontWeight: 800, letterSpacing: 0.2 }}>
              ATS Analyzer
            </Link>
            <span className="muted">HR + Individual</span>
          </div>
          <div className="row">
            {email ? <span className="muted">{email}</span> : null}
            <Link className="btn btn-ghost" to="/select-mode">
              Mode
            </Link>
            <button
              className="btn btn-danger"
              onClick={() => {
                clearSession()
                navigate('/login')
              }}
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

