import api from './api'

export async function uploadResume(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/api/upload-resume', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return res.data
}

export async function hrAnalyzeBatch({ resumes, job_description, required_skills }) {
  const res = await api.post('/api/hr/analyze-batch', { resumes, job_description, required_skills })
  return res.data
}

export async function individualAnalyze(payload) {
  const res = await api.post('/api/individual/analyze-resume', payload)
  return res.data
}

export async function optimizeResume(payload) {
  const res = await api.post('/api/individual/optimize-resume', payload)
  return res.data
}

export async function generateReport(payload) {
  const res = await api.post('/api/generate-report', payload)
  return res.data
}

