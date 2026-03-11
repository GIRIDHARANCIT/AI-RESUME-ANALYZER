import api from './api'

export async function sendOtp(email) {
  const res = await api.post('/api/auth/send-otp', { email })
  return res.data
}

export async function verifyOtp(email, otp) {
  const res = await api.post('/api/auth/verify-otp', { email, otp })
  return res.data
}

export async function checkUserExists(email) {
  const res = await api.post('/api/auth/check-user', { email })
  return res.data.exists
}

export async function loginWithPassword(email, password) {
  const res = await api.post('/api/auth/login-password', { email, password })
  return res.data
}

export async function setPasswordAfterOtp(email, password) {
  const res = await api.post('/api/auth/set-password-otp', { email, password })
  return res.data
}

export async function resetPasswordWithOtp(email, password) {
  const res = await api.post('/api/auth/reset-password-otp', { email, password })
  return res.data
}

export function setSession(sessionId, email) {
  localStorage.setItem('session_id', sessionId)
  localStorage.setItem('email', email)
}

export function clearSession() {
  localStorage.removeItem('session_id')
  localStorage.removeItem('email')
  localStorage.removeItem('pending_email')
  localStorage.removeItem('is_new_user')
  localStorage.removeItem('is_password_reset')
}

export function isAuthed() {
  return Boolean(localStorage.getItem('session_id'))
}


