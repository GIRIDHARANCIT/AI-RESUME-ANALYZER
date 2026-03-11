import { Link, useNavigate } from 'react-router-dom'
import { useMemo, useState } from 'react'

import { TopNav } from '../components/TopNav'

export function AnalysisResultsPage() {
  const navigate = useNavigate()
  const stored = localStorage.getItem('individual_results')
  const data = stored ? JSON.parse(stored) : null

  const [showRaw, setShowRaw] = useState(false)

  const chart = useMemo(() => {
    const b = data?.breakdown || {}
    return [
      { k: 'keyword_match', v: b.keyword_match ?? 0 },
      { k: 'skills_match', v: b.skills_match ?? 0 },
      { k: 'experience_relevance', v: b.experience_relevance ?? 0 },
      { k: 'formatting_quality', v: b.formatting_quality ?? 0 },
    ]
  }, [data])

  if (!data) {
    return (
      <>
        <TopNav />
        <div className="container">
          <div className="card" style={{ padding: 18 }}>
            <h2 style={{ marginTop: 0 }}>Analysis Results</h2>
            <p className="muted">No results found. Run an Individual analysis first.</p>
            <button className="btn btn-primary" onClick={() => navigate('/individual')}>
              Go to Individual Dashboard
            </button>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="grid" style={{ gridTemplateColumns: '1fr' }}>
          <div className="card" style={{ padding: 18 }}>
            <h2 style={{ marginTop: 0 }}>ATS Score: {Number(data.ats_score ?? 0).toFixed(1)} / 100</h2>
            <div className="muted">{data.overall_score_explanation}</div>

            <div className="card" style={{ padding: 12, marginTop: 14, background: 'rgba(255,255,255,.04)' }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>Breakdown</div>
              {chart.map((x) => (
                <div key={x.k} className="row" style={{ justifyContent: 'space-between', marginBottom: 6 }}>
                  <div className="muted" style={{ textTransform: 'capitalize' }}>
                    {x.k.replaceAll('_', ' ')}
                  </div>
                  <div style={{ fontWeight: 700 }}>{Number(x.v).toFixed(1)}%</div>
                </div>
              ))}
            </div>

            <div className="row" style={{ marginTop: 14 }}>
              <button
                className="btn btn-primary"
                onClick={() => {
                  localStorage.setItem(
                    'editor_seed',
                    JSON.stringify({
                      resume_text: data.resume_text || '',
                      suggestions_raw: data.suggestions_raw || {},
                      file_suffix: data.file_suffix || '.pdf',
                    }),
                  )
                  navigate('/editor')
                }}
              >
                Open Resume Optimizer
              </button>
              <Link className="btn btn-ghost" to="/individual">
                Analyze another
              </Link>
            </div>
          </div>

          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Highlights & Insights</h3>
            <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', gap: 14 }}>
              <div className="card" style={{ padding: 12, background: 'rgba(255,255,255,.04)' }}>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Strengths</div>
                <ul>
                  {(data.strengths || []).slice(0, 5).map((s, i) => (
                    <li key={i} className="muted">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="card" style={{ padding: 12, background: 'rgba(255,255,255,.04)' }}>
                <div style={{ fontWeight: 700, marginBottom: 8 }}>Weaknesses</div>
                <ul>
                  {(data.weaknesses || []).slice(0, 5).map((s, i) => (
                    <li key={i} className="muted">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="card" style={{ padding: 12, marginTop: 12, background: 'rgba(255,255,255,.04)' }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>Missing skills / keywords</div>
              <div className="muted">
                {(data.missing_skills || []).slice(0, 15).join(', ') || '—'}
              </div>
            </div>

            <div className="card" style={{ padding: 12, marginTop: 12, background: 'rgba(255,255,255,.04)' }}>
              <div className="row" style={{ justifyContent: 'space-between', marginBottom: 8 }}>
                <div style={{ fontWeight: 700 }}>Improvement Suggestions</div>
                <button className="btn btn-ghost" onClick={() => setShowRaw((v) => !v)} style={{ fontSize: 12 }}>
                  {showRaw ? 'Hide raw' : 'Show raw'}
                </button>
              </div>
              <ul>
                {(data.improvement_suggestions || []).slice(0, 6).map((s, i) => (
                  <li key={i} className="muted">
                    {s}
                  </li>
                ))}
              </ul>
              {showRaw ? (
                <pre style={{ margin: '12px 0 0 0', whiteSpace: 'pre-wrap', fontSize: 11 }} className="muted">
                  {JSON.stringify(data.suggestions_raw || {}, null, 2)}
                </pre>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

