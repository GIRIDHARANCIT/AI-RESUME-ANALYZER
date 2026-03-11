import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { sendOtp, loginWithPassword, checkUserExists } from '../services/auth'

export function LoginPage() {
  const [email, setEmail] = useState(localStorage.getItem('email') || '')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mode, setMode] = useState('login') // 'login', 'password', 'forgot'
  const [userExists, setUserExists] = useState(null)
  const navigate = useNavigate()

  async function handleEmailSubmit() {
    setError('')
    if (!email.includes('@')) {
      setError('Enter a valid email.')
      return
    }
    setLoading(true)
    try {
      const exists = await checkUserExists(email)
      setUserExists(exists)
      if (exists) {
        setMode('password')
      } else {
        setMode('password') // New user creates password
      }
    } catch (e) {
      setError('Unable to check email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  async function handlePasswordLogin() {
    setError('')
    if (!password) {
      setError('Enter your password.')
      return
    }
    setLoading(true)
    try {
      const result = await loginWithPassword(email, password)
      if (result.requires_otp) {
        // New user - send OTP for 2FA
        localStorage.setItem('pending_email', email)
        localStorage.setItem('session_id', result.temp_session)
        localStorage.setItem('is_new_user', 'true')
        navigate('/otp')
      } else {
        // Existing user - direct login
        localStorage.setItem('session_id', result.session_id)
        localStorage.setItem('email', email)
        navigate('/dashboard')
      }
    } catch (e) {
      setError(e?.response?.data?.detail || 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  async function handleForgotPassword() {
    setError('')
    if (!email.includes('@')) {
      setError('Enter a valid email.')
      return
    }
    setLoading(true)
    try {
      await sendOtp(email)
      localStorage.setItem('pending_email', email)
      localStorage.setItem('is_password_reset', 'true')
      navigate('/otp')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to send OTP.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px' }}>
      <div className="card" style={{ padding: 28, maxWidth: 400 }}>
        {mode === 'login' && (
          <>
            <h2 style={{ marginTop: 0, textAlign: 'center' }}>Login</h2>
            <p className="muted" style={{ marginTop: 6, textAlign: 'center' }}>
              Enter your Gmail to get started
            </p>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Email</label>
              <input
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@gmail.com"
                onKeyPress={(e) => e.key === 'Enter' && handleEmailSubmit()}
              />
            </div>
            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={handleEmailSubmit} disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Checking…' : 'Continue'}
              </button>
              <button className="btn btn-ghost" onClick={() => navigate('/')} style={{ width: '100%' }}>
                Back
              </button>
            </div>
          </>
        )}

        {mode === 'password' && (
          <>
            <h2 style={{ marginTop: 0, textAlign: 'center' }}>
              {userExists ? 'Enter Password' : 'Create Password'}
            </h2>
            <p className="muted" style={{ marginTop: 6, textAlign: 'center' }}>
              {email}
            </p>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Password</label>
              <input
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                onKeyPress={(e) => e.key === 'Enter' && handlePasswordLogin()}
              />
            </div>
            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={handlePasswordLogin} disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Logging in…' : 'Login'}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setMode('forgot')
                  setPassword('')
                  setError('')
                }}
                style={{ width: '100%' }}
              >
                Forgot Password?
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setMode('login')
                  setPassword('')
                  setError('')
                }}
                style={{ width: '100%' }}
              >
                Back
              </button>
            </div>
            {!userExists && (
              <p className="muted" style={{ marginTop: 14, fontSize: 12, textAlign: 'center' }}>
                You're a new user. Create a password and verify via OTP.
              </p>
            )}
          </>
        )}

        {mode === 'forgot' && (
          <>
            <h2 style={{ marginTop: 0, textAlign: 'center' }}>Reset Password</h2>
            <p className="muted" style={{ marginTop: 6, textAlign: 'center' }}>
              We'll send an OTP to verify your identity
            </p>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Email</label>
              <input
                className="input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@gmail.com"
              />
            </div>
            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={handleForgotPassword} disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Sending OTP…' : 'Send OTP'}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setMode('password')
                  setError('')
                }}
                style={{ width: '100%' }}
              >
                Back to Login
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

