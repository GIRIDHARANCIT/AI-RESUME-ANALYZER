import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Dropzone from 'react-dropzone'

import { TopNav } from '../components/TopNav'
import { individualAnalyze, uploadResume } from '../services/resume'

export function IndividualDashboardPage() {
  const navigate = useNavigate()
  const [resume, setResume] = useState(null)
  const [targetPosition, setTargetPosition] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [generalAts, setGeneralAts] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function onDrop(files) {
    setError('')
    setLoading(true)
    try {
      const u = await uploadResume(files[0])
      setResume(u)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  async function analyze() {
    setError('')
    if (!resume?.extracted_text) return setError('Upload your resume first.')
    setLoading(true)
    try {
      const res = await individualAnalyze({
        resume_text: resume.extracted_text,
        target_position: targetPosition || null,
        company_name: companyName || null,
        job_description: generalAts ? null : jobDescription || null,
        general_ats: generalAts,
      })
      localStorage.setItem('individual_results', JSON.stringify({ 
        ...res, 
        resume_text: resume.extracted_text,
        file_suffix: resume.suffix || '.pdf',
        original_filename: resume.filename,
      }))
      navigate('/individual/results')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="grid" style={{ gridTemplateColumns: '1.1fr 0.9fr' }}>
          <div className="card" style={{ padding: 18 }}>
            <h2 style={{ marginTop: 0 }}>Individual Dashboard</h2>
            <p className="muted">Upload your resume and get ATS score + Gemini suggestions (with fallback if AI is off).</p>

            <Dropzone onDrop={onDrop} multiple={false}>
              {({ getRootProps, getInputProps, isDragActive }) => (
                <div
                  {...getRootProps()}
                  className="card"
                  style={{
                    padding: 18,
                    borderStyle: 'dashed',
                    borderColor: isDragActive ? 'rgba(37,99,235,.8)' : 'rgba(255,255,255,.18)',
                    background: 'rgba(255,255,255,.04)',
                    cursor: 'pointer',
                    marginTop: 12,
                  }}
                >
                  <input {...getInputProps()} />
                  <div style={{ fontWeight: 700 }}>{resume ? 'Resume uploaded' : 'Drag & drop your resume'}</div>
                  <div className="muted" style={{ marginTop: 6 }}>
                    {resume?.filename || 'Any file type'}
                  </div>
                </div>
              )}
            </Dropzone>

            <div className="grid" style={{ marginTop: 14 }}>
              <div className="row" style={{ justifyContent: 'space-between' }}>
                <label className="muted" style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                  <input type="checkbox" checked={generalAts} onChange={(e) => setGeneralAts(e.target.checked)} />
                  General ATS evaluation (no job description)
                </label>
              </div>

              <div>
                <label className="muted">Target job position</label>
                <input className="input" value={targetPosition} onChange={(e) => setTargetPosition(e.target.value)} placeholder="e.g., Frontend Developer" />
              </div>
              <div>
                <label className="muted">Company name</label>
                <input className="input" value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="e.g., Google" />
              </div>
              {!generalAts ? (
                <div>
                  <label className="muted">Job description</label>
                  <textarea rows={8} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
                </div>
              ) : null}
            </div>

            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}

            <div className="row" style={{ marginTop: 14 }}>
              <button className="btn btn-primary" onClick={analyze} disabled={loading}>
                {loading ? 'Analyzing…' : 'Analyze'}
              </button>
              <button className="btn btn-ghost" onClick={() => setResume(null)} disabled={loading}>
                Clear
              </button>
            </div>
          </div>

          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Preview</h3>
            <div className="muted" style={{ fontSize: 13 }}>
              Extracted text (first 1200 chars)
            </div>
            <div className="card" style={{ padding: 12, marginTop: 10, background: 'rgba(255,255,255,.04)', maxHeight: 420, overflow: 'auto' }}>
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }}>
                {(resume?.extracted_text || '').slice(0, 1200) || '—'}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

