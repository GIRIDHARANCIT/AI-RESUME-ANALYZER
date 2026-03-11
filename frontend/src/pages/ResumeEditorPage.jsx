import { useMemo, useState } from 'react'

import { TopNav } from '../components/TopNav'
import { optimizeResume } from '../services/resume'

export function ResumeEditorPage() {
  const seedRaw = localStorage.getItem('editor_seed')
  const seed = seedRaw ? JSON.parse(seedRaw) : { resume_text: '', suggestions_raw: {}, file_suffix: '.pdf' }

  const [resumeText, setResumeText] = useState(seed.resume_text || '')
  const [userEdits, setUserEdits] = useState({})
  const [optimized, setOptimized] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [downloading, setDownloading] = useState(false)

  const suggestions = useMemo(() => seed.suggestions_raw || {}, [seed])
  const fileSuffix = seed.file_suffix || '.pdf'

  async function runOptimize() {
    setError('')
    setLoading(true)
    try {
      const res = await optimizeResume({
        resume_text: resumeText,
        suggestions,
        user_edits: userEdits,
      })
      setOptimized(res.optimized_text || '')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Optimization failed (Gemini key may be missing).')
    } finally {
      setLoading(false)
    }
  }

  function downloadFile(format) {
    if (!optimized.trim()) return
    setDownloading(true)
    const base = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const endpoint = format === 'pdf' ? '/api/individual/download-optimized-pdf' : 
                     format === 'docx' ? '/api/individual/download-optimized-docx' :
                     '/api/individual/download-optimized-txt'
    
    fetch(base + endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ optimized_text: optimized }),
    })
      .then((r) => r.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        const ext = format === 'pdf' ? '.pdf' : format === 'docx' ? '.docx' : '.txt'
        a.download = `Optimized_Resume${ext}`
        a.click()
        window.URL.revokeObjectURL(url)
      })
      .catch(() => setError('Download failed'))
      .finally(() => setDownloading(false))
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="card" style={{ padding: 18 }}>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <div>
              <h2 style={{ marginTop: 0 }}>Resume Optimizer</h2>
              <div className="muted">Edit suggestions, modify resume text, generate optimized resume, download PDF.</div>
            </div>
            <div className="row">
              <button className="btn btn-primary" onClick={runOptimize} disabled={loading}>
                {loading ? 'Generating…' : 'Generate optimized resume'}
              </button>
              <button className="btn btn-ghost" onClick={() => setOptimized('')} disabled={loading}>
                Clear output
              </button>
            </div>
          </div>

          {error ? (
            <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
              <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
            </div>
          ) : null}

          <div className="grid" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 14 }}>
            <div>
              <label className="muted">Resume text</label>
              <textarea rows={18} value={resumeText} onChange={(e) => setResumeText(e.target.value)} />
            </div>
            <div>
              <label className="muted">Optimized output</label>
              <textarea rows={18} value={optimized} onChange={(e) => setOptimized(e.target.value)} placeholder="Click 'Generate optimized resume'…" />
              <div className="row" style={{ marginTop: 10, gap: 8, flexWrap: 'wrap' }}>
                <button 
                  className="btn btn-primary" 
                  onClick={() => downloadFile('pdf')} 
                  disabled={!optimized.trim() || downloading}
                >
                  Download as PDF
                </button>
                <button 
                  className="btn btn-primary" 
                  onClick={() => downloadFile('docx')} 
                  disabled={!optimized.trim() || downloading}
                >
                  Download as DOCX
                </button>
                <button 
                  className="btn btn-primary" 
                  onClick={() => downloadFile('txt')} 
                  disabled={!optimized.trim() || downloading}
                >
                  Download as TXT
                </button>
                {fileSuffix && fileSuffix !== '.pdf' ? (
                  <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                    Original format: {fileSuffix.toUpperCase()}
                  </div>
                ) : null}
              </div>
            </div>
          </div>

          <div className="card" style={{ padding: 12, marginTop: 14, background: 'rgba(255,255,255,.04)' }}>
            <div style={{ fontWeight: 700, marginBottom: 8 }}>Suggestions (raw)</div>
            <pre className="muted" style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
              {JSON.stringify(suggestions, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </>
  )
}

