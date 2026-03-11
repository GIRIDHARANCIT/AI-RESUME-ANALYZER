import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { setSession, verifyOtp, setPasswordAfterOtp, resetPasswordWithOtp } from '../services/auth'

export function OtpPage() {
  const navigate = useNavigate()
  const email = useMemo(() => localStorage.getItem('pending_email') || '', [])
  const isNewUser = localStorage.getItem('is_new_user') === 'true'
  const isPasswordReset = localStorage.getItem('is_password_reset') === 'true'
  
  const [otp, setOtp] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState('otp') // 'otp' or 'password'

  async function onVerifyOtp() {
    setError('')
    if (!email) {
      setError('Missing email. Go back to login.')
      return
    }
    if (otp.trim().length < 4) {
      setError('Enter the OTP from your email.')
      return
    }
    setLoading(true)
    try {
      const res = await verifyOtp(email, otp.trim())
      if (isNewUser || isPasswordReset) {
        // New user or password reset - go to set password step
        setStep('password')
      } else {
        // Regular OTP login
        setSession(res.session_id, email)
        localStorage.removeItem('pending_email')
        navigate('/select-mode')
      }
    } catch (e) {
      setError(e?.response?.data?.detail || 'OTP verification failed.')
    } finally {
      setLoading(false)
    }
  }

  async function onSetPassword() {
    setError('')
    if (!newPassword) {
      setError('Enter a password.')
      return
    }
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    try {
      let res
      if (isPasswordReset) {
        res = await resetPasswordWithOtp(email, newPassword)
      } else {
        res = await setPasswordAfterOtp(email, newPassword)
      }
      setSession(res.session_id, email)
      localStorage.removeItem('pending_email')
      localStorage.removeItem('is_new_user')
      localStorage.removeItem('is_password_reset')
      navigate('/select-mode')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to set password.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: '20px' }}>
      <div className="card" style={{ padding: 28, maxWidth: 400 }}>
        {step === 'otp' && (
          <>
            <h2 style={{ marginTop: 0, textAlign: 'center' }}>Verify OTP</h2>
            <p className="muted" style={{ marginTop: 6, textAlign: 'center' }}>
              {email}
            </p>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Enter OTP from email</label>
              <input
                className="input"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="6-digit OTP"
                onKeyPress={(e) => e.key === 'Enter' && onVerifyOtp()}
              />
            </div>
            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={onVerifyOtp} disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Verifying…' : 'Verify OTP'}
              </button>
              <button className="btn btn-ghost" onClick={() => navigate('/login')} style={{ width: '100%' }}>
                Back to Login
              </button>
            </div>
          </>
        )}

        {step === 'password' && (
          <>
            <h2 style={{ marginTop: 0, textAlign: 'center' }}>
              {isPasswordReset ? 'Reset Password' : 'Create Password'}
            </h2>
            <p className="muted" style={{ marginTop: 6, textAlign: 'center' }}>
              {email}
            </p>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Password</label>
              <input
                className="input"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
              />
            </div>
            <div style={{ marginTop: 14 }}>
              <label className="muted">Confirm Password</label>
              <input
                className="input"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                onKeyPress={(e) => e.key === 'Enter' && onSetPassword()}
              />
            </div>
            {error ? (
              <div className="card" style={{ padding: 12, marginTop: 12, borderColor: 'rgba(239,68,68,.35)' }}>
                <div style={{ color: '#fecaca', fontWeight: 600 }}>{error}</div>
              </div>
            ) : null}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 20 }}>
              <button className="btn btn-primary" onClick={onSetPassword} disabled={loading} style={{ width: '100%' }}>
                {loading ? 'Setting Password…' : 'Continue'}
              </button>
              <button
                className="btn btn-ghost"
                onClick={() => {
                  setStep('otp')
                  setNewPassword('')
                  setConfirmPassword('')
                  setError('')
                }}
                style={{ width: '100%' }}
              >
                Back
              </button>
            </div>
            <p className="muted" style={{ marginTop: 14, fontSize: 12, textAlign: 'center' }}>
              Password must be at least 6 characters long.
            </p>
          </>
        )}
      </div>
    </div>
  )
}

