import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './components/LoginPage'
import Dashboard from './components/Dashboard'
import RegisterUserPage from './components/RegisterUserPage'
import RecognitionPage from './components/RecognitionPage'
import UsersPage from './components/UsersPage'
import LogsPage from './components/LogsPage'
import './App.css'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    setLoading(false)
  }, [])

  if (loading) {
    return <div className="loading">Loading...</div>
  }

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={<LoginPage onLogin={() => setIsAuthenticated(true)} />} 
        />
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Dashboard onLogout={() => setIsAuthenticated(false)} />
            ) : (
              <Navigate to="/login" />
            )
          }
        >
          <Route index element={<Navigate to="/register" replace />} />
          <Route path="register" element={<RegisterUserPage />} />
          <Route path="recognition" element={<RecognitionPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="logs" element={<LogsPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App

