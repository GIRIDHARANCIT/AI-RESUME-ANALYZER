import './App.css'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import { LandingPage } from './pages/LandingPage'
import { LoginPage } from './pages/LoginPage'
import { OtpPage } from './pages/OtpPage'
import { DashboardSelectorPage } from './pages/DashboardSelectorPage'
import { HrDashboardPage } from './pages/HrDashboardPage'
import { HrResultsPage } from './pages/HrResultsPage'
import { IndividualDashboardPage } from './pages/IndividualDashboardPage'
import { AnalysisResultsPage } from './pages/AnalysisResultsPage'
import { ResumeEditorPage } from './pages/ResumeEditorPage'
import { ProtectedRoute } from './components/ProtectedRoute'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/otp" element={<OtpPage />} />

        <Route
          path="/select-mode"
          element={
            <ProtectedRoute>
              <DashboardSelectorPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/hr"
          element={
            <ProtectedRoute>
              <HrDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/hr/results"
          element={
            <ProtectedRoute>
              <HrResultsPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/individual"
          element={
            <ProtectedRoute>
              <IndividualDashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/individual/results"
          element={
            <ProtectedRoute>
              <AnalysisResultsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/editor"
          element={
            <ProtectedRoute>
              <ResumeEditorPage />
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
