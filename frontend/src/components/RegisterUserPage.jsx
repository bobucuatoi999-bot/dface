import React, { useState, useRef, useEffect } from 'react'
import { usersAPI } from '../services/api'
import { startCamera, stopCamera, captureFrame, imageToBase64 } from '../utils/camera'
import './RegisterUserPage.css'

function RegisterUserPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [capturedImage, setCapturedImage] = useState(null)
  
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const [cameraActive, setCameraActive] = useState(false)

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        stopCamera(streamRef.current)
      }
    }
  }, [])

  const startVideo = async () => {
    try {
      const stream = await startCamera(videoRef.current)
      streamRef.current = stream
      setCameraActive(true)
    } catch (error) {
      setError('Could not access camera. Please allow camera permissions.')
    }
  }

  const stopVideo = () => {
    if (streamRef.current) {
      stopCamera(streamRef.current)
      streamRef.current = null
      setCameraActive(false)
    }
  }

  const capturePhoto = async () => {
    if (!videoRef.current) return
    
    try {
      const imageData = await captureFrame(videoRef.current)
      setCapturedImage(imageData)
      stopVideo()
    } catch (error) {
      setError('Failed to capture image')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    if (!capturedImage) {
      setError('Please capture a photo first')
      setLoading(false)
      return
    }

    try {
      const base64Image = imageToBase64(capturedImage)
      const user = await usersAPI.register(name, email || undefined, base64Image)
      
      setSuccess(`User "${user.name}" registered successfully! (ID: ${user.id})`)
      setName('')
      setEmail('')
      setEmployeeId('')
      setCapturedImage(null)
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Registration failed'
      setError(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-page">
      <h1 className="page-title">Register New User</h1>
      <p className="page-subtitle">Capture face and register user in the system</p>

      <div className="register-container">
        <div className="register-card">
          <form onSubmit={handleSubmit}>
            <div className="form-section">
              <h3>User Information</h3>
              
              <div className="form-group">
                <label>Full Name *</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="John Doe"
                />
              </div>

              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="john.doe@example.com"
                />
              </div>

              <div className="form-group">
                <label>Employee ID</label>
                <input
                  type="text"
                  value={employeeId}
                  onChange={(e) => setEmployeeId(e.target.value)}
                  placeholder="EMP-12345"
                />
              </div>
            </div>

            <div className="form-section">
              <h3>Face Capture</h3>
              
              <div className="camera-section">
                {!capturedImage ? (
                  <>
                    <video
                      ref={videoRef}
                      autoPlay
                      playsInline
                      className="camera-preview"
                      style={{ display: cameraActive ? 'block' : 'none' }}
                    />
                    
                    {!cameraActive && (
                      <div className="camera-placeholder">
                        <div className="placeholder-icon">📷</div>
                        <p>Camera not started</p>
                      </div>
                    )}

                    <div className="camera-controls">
                      {!cameraActive ? (
                        <button type="button" onClick={startVideo} className="btn-primary">
                          📹 Start Camera
                        </button>
                      ) : (
                        <>
                          <button type="button" onClick={capturePhoto} className="btn-primary">
                            📸 Capture Photo
                          </button>
                          <button type="button" onClick={stopVideo} className="btn-secondary">
                            ⏹ Stop Camera
                          </button>
                        </>
                      )}
                    </div>
                  </>
                ) : (
                  <div className="captured-image-container">
                    <img src={capturedImage} alt="Captured" className="captured-image" />
                    <button
                      type="button"
                      onClick={() => {
                        setCapturedImage(null)
                        startVideo()
                      }}
                      className="btn-secondary"
                    >
                      🔄 Retake Photo
                    </button>
                  </div>
                )}
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button type="submit" className="btn-primary btn-submit" disabled={loading || !capturedImage}>
              {loading ? 'Registering...' : '✅ Register User'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default RegisterUserPage

