import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Dropzone from 'react-dropzone'

import { TopNav } from '../components/TopNav'
import { hrAnalyzeBatch, uploadResume } from '../services/resume'

export function HrDashboardPage() {
  const navigate = useNavigate()
  const [uploads, setUploads] = useState([])
  const [jobDescription, setJobDescription] = useState('')
  const [skills, setSkills] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const requiredSkills = useMemo(
    () =>
      skills
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    [skills],
  )

  async function onDrop(files) {
    setError('')
    setLoading(true)
    try {
      const results = []
      for (const f of files) results.push(await uploadResume(f))
      setUploads((prev) => [...prev, ...results])
    } catch (e) {
      setError(e?.response?.data?.detail || 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  async function analyze() {
    setError('')
    if (!uploads.length) return setError('Upload at least one resume.')
    if (!jobDescription.trim()) return setError('Job description is required.')
    setLoading(true)
    try {
      const res = await hrAnalyzeBatch({
        resumes: uploads.map((u) => ({
          file_id: u.file_id,
          filename: u.filename,
          extracted_text: u.extracted_text,
          candidate_name: u.candidate_name,
        })),
        job_description: jobDescription,
        required_skills: requiredSkills,
      })
      localStorage.setItem('hr_results', JSON.stringify(res))
      navigate('/hr/results')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Batch analysis failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <TopNav />
      <div className="container">
        <div className="grid" style={{ gridTemplateColumns: '1.2fr 0.8fr' }}>
          <div className="card" style={{ padding: 18 }}>
            <h2 style={{ marginTop: 0 }}>HR Dashboard</h2>
            <p className="muted">Upload multiple PDF/DOCX resumes and analyze against a job description.</p>

            <Dropzone onDrop={onDrop} multiple>
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
                  <div style={{ fontWeight: 700 }}>Drag & drop resumes here</div>
                  <div className="muted" style={{ marginTop: 6 }}>
                    Or click to select files. (All file types accepted)
                  </div>
                </div>
              )}
            </Dropzone>

            <div className="grid" style={{ marginTop: 14 }}>
              <div>
                <label className="muted">Job description</label>
                <textarea rows={8} value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} />
              </div>
              <div>
                <label className="muted">Required skills (comma-separated)</label>
                <input className="input" value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="react, fastapi, python, aws" />
              </div>
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
              <button className="btn btn-ghost" onClick={() => setUploads([])} disabled={loading}>
                Clear uploads
              </button>
            </div>
          </div>

          <div className="card" style={{ padding: 18 }}>
            <h3 style={{ marginTop: 0 }}>Uploaded candidates</h3>
            <div className="muted">{uploads.length} file(s)</div>
            <div style={{ marginTop: 10, display: 'grid', gap: 10 }}>
              {uploads.map((u) => (
                <div key={u.file_id} className="card" style={{ padding: 12, background: 'rgba(255,255,255,.04)' }}>
                  <div style={{ fontWeight: 700, fontSize: 13 }}>{u.filename}</div>
                  <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                    {/* Names will show in the report */}
                  </div>
                </div>
              ))}
              {!uploads.length ? <div className="muted" style={{ marginTop: 8 }}>No uploads yet.</div> : null}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

