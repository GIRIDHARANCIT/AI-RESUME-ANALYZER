import { Navigate } from 'react-router-dom'
import { isAuthed } from '../services/auth'

export function ProtectedRoute({ children }) {
  if (!isAuthed()) return <Navigate to="/login" replace />
  return children
}

