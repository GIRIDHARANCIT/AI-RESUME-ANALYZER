import { useMemo, useState } from 'react'

import { TopNav } from '../components/TopNav'
import { generateReport } from '../services/resume'

export function HrResultsPage() {
  const stored = localStorage.getItem('hr_results')
  const payload = stored ? JSON.parse(stored) : null
  const candidates = payload?.candidates || []

  const [query, setQuery] = useState('')
  const [minScore, setMinScore] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [reportId, setReportId] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return [...candidates]
      .filter((c) => (c.ats_score ?? 0) >= Number(minScore || 0))
      .filter((c) => (q ? ((c.applicant_name || c.candidate_name || '').toLowerCase().includes(q)) : true))
      .sort((a, b) => (b.ats_score ?? 0) - (a.ats_score ?? 0))
  }, [candidates, query, minScore])

  async function onGenerateReport() {
    setError('')
    setLoading(true)
    try {
      const res = await generateReport({
        job_description: payload?.job_description || '',
        job_summary: (payload?.job_description || '').slice(0, 600),
        candidates: filtered,
      })
      setReportId(res.report_id)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Report generation failed.')
    } finally {
      setLoading(false)
    }
  }

  if (!payload) {
    return (
      <>
        <TopNav />
        <div className="container">
          <div className="card" style={{ padding: 18 }}>
            <h2 style={{ marginTop: 0 }}>HR Results</h2>
            <p className="muted">No results found. Run an HR batch analysis first.</p>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="card" style={{ padding: 18 }}>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <div>
              <h2 style={{ marginTop: 0 }}>HR Results</h2>
              <div className="muted">Sorted by ATS score (descending)</div>
            </div>
            <div className="row">
              <button className="btn btn-primary" onClick={onGenerateReport} disabled={loading || !filtered.length}>
                {loading ? 'Generating…' : 'Download PDF report'}
              </button>
              {reportId ? (
                <a className="btn btn-ghost" href={(import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') + `/api/download-report/${reportId}`} target="_blank" rel="noreferrer">
                  Open report
                </a>
              ) : null}
            </div>
          </div>

          <div className="row" style={{ marginTop: 14 }}>
            <input className="input" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search candidate name…" style={{ maxWidth: 320 }} />
            <input className="input" type="number" value={minScore} onChange={(e) => setMinScore(e.target.value)} placeholder="Min score" style={{ width: 140 }} />
            <div className="muted">{filtered.length} candidate(s)</div>
          </div>

          {error ? (
            <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
              <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
            </div>
          ) : null}

          <div style={{ overflowX: 'auto', marginTop: 14 }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left' }}>
                  <th style={{ padding: 10 }} className="muted">
                    Candidate
                  </th>
                  <th style={{ padding: 10 }} className="muted">
                    ATS Score
                  </th>
                  <th style={{ padding: 10 }} className="muted">
                    Skill Match %
                  </th>
                  <th style={{ padding: 10 }} className="muted">
                    Missing Skills
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((c) => (
                  <tr key={c.file_id} style={{ borderTop: '1px solid rgba(255,255,255,.08)' }}>
                    <td style={{ padding: 10, fontWeight: 700 }}>{c.applicant_name || c.candidate_name}</td>
                    <td style={{ padding: 10 }}>{Number(c.ats_score).toFixed(1)}</td>
                    <td style={{ padding: 10 }}>{Number(c.skills_match_pct ?? 0).toFixed(1)}%</td>
                    <td style={{ padding: 10 }} className="muted">
                      {(c.missing_skills || []).slice(0, 8).join(', ') || '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}

