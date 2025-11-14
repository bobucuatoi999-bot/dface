import React, { useState, useRef, useEffect } from 'react'
import { usersAPI } from '../services/api'
import { startCamera, stopCamera, startVideoRecording, videoBlobToBase64, captureFrame, imageToBase64 } from '../utils/camera'
import './RegisterUserPage.css'

function RegisterUserPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [employeeId, setEmployeeId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [recordedVideo, setRecordedVideo] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [videoDuration, setVideoDuration] = useState(0)
  const [validationInfo, setValidationInfo] = useState(null)
  const [facesDetected, setFacesDetected] = useState([])
  const [faceDetectionStatus, setFaceDetectionStatus] = useState(null) // 'detecting', 'detected', 'none'
  
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const recorderRef = useRef(null)
  const timerRef = useRef(null)
  const canvasRef = useRef(null)
  const detectionIntervalRef = useRef(null)
  const [cameraActive, setCameraActive] = useState(false)

  useEffect(() => {
    return () => {
      if (streamRef.current) {
        stopCamera(streamRef.current)
      }
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current)
      }
    }
  }, [])

  // Draw face detection boxes on canvas
  const drawFaceBoxes = (faces) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video || !video.videoWidth || !video.videoHeight) return
    
    const ctx = canvas.getContext('2d')
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    if (faces && faces.length > 0) {
      faces.forEach((face) => {
        const [top, right, bottom, left] = face.bbox
        const width = right - left
        const height = bottom - top
        
        // Draw bounding box
        ctx.strokeStyle = '#00ff00' // Green for detected face
        ctx.lineWidth = 3
        ctx.strokeRect(left, top, width, height)
        
        // Draw label background
        ctx.fillStyle = '#00ff00'
        ctx.fillRect(left, top - 25, Math.max(120, 100), 25)
        
        // Draw label text
        ctx.fillStyle = 'white'
        ctx.font = 'bold 14px sans-serif'
        ctx.fillText('Face Detected', left + 5, top - 8)
      })
      setFaceDetectionStatus('detected')
    } else {
      setFaceDetectionStatus('none')
    }
  }

  // Detect faces in video frame
  const detectFacesInFrame = async () => {
    if (!videoRef.current || !isRecording || !cameraActive) return
    
    try {
      // Capture frame
      const imageData = await captureFrame(videoRef.current)
      const base64Image = imageToBase64(imageData)
      
      // Call face detection API
      const result = await usersAPI.detectFaces(base64Image)
      
      if (result && result.faces) {
        setFacesDetected(result.faces)
        drawFaceBoxes(result.faces)
      } else {
        setFacesDetected([])
        drawFaceBoxes([])
      }
    } catch (error) {
      // Silently handle errors to avoid interrupting recording
      console.error('Face detection error:', error)
      setFaceDetectionStatus(null)
    }
  }

  const startVideo = async () => {
    try {
      setError('')
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
    if (recorderRef.current && recorderRef.current.state === 'recording') {
      recorderRef.current.stop()
    }
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current)
      detectionIntervalRef.current = null
    }
    setIsRecording(false)
    setRecordingTime(0)
    // Clear canvas
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
    setFacesDetected([])
    setFaceDetectionStatus(null)
  }

  const startRecording = async () => {
    if (!videoRef.current || !cameraActive) {
      setError('Please start camera first')
      return
    }

    try {
      setError('')
      setValidationInfo(null)
      setIsRecording(true)
      setRecordingTime(0)
      setVideoDuration(0)

      // Start video recording (7 seconds duration)
      const { recorder, promise } = startVideoRecording(videoRef.current, {
        duration: 7000,
        mimeType: 'video/webm;codecs=vp8,opus'
      })
      
      recorderRef.current = recorder

      // Start recording timer for UI feedback
      let currentTime = 0
      timerRef.current = setInterval(() => {
        currentTime += 0.1
        setRecordingTime(currentTime)
        if (currentTime >= 7.0) {
          // Stop timer at 7 seconds
          if (timerRef.current) {
            clearInterval(timerRef.current)
            timerRef.current = null
          }
        }
      }, 100)

      // Start face detection during recording (every 300ms = ~3 FPS)
      setFaceDetectionStatus('detecting')
      detectionIntervalRef.current = setInterval(() => {
        detectFacesInFrame()
      }, 300)

      // Wait for recording to complete (will auto-stop at 7 seconds)
      const videoBlob = await promise
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      
      // Stop face detection
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current)
        detectionIntervalRef.current = null
      }
      
      // Clear canvas
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
      
      // Store final duration (7 seconds)
      setVideoDuration(7.0)
      setRecordingTime(7.0)
      setIsRecording(false)
      
      // Convert to base64
      const videoBase64 = await videoBlobToBase64(videoBlob)
      setRecordedVideo(videoBase64)
      
      // Stop camera after recording
      stopVideo()
      
      // Reset face detection
      setFacesDetected([])
      setFaceDetectionStatus(null)
    } catch (error) {
      console.error('Recording error:', error)
      setError('Failed to record video: ' + error.message)
      setIsRecording(false)
      setRecordingTime(0)
      setVideoDuration(0)
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current)
        detectionIntervalRef.current = null
      }
      // Clear canvas
      const canvas = canvasRef.current
      if (canvas) {
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvas.width, canvas.height)
      }
      setFacesDetected([])
      setFaceDetectionStatus(null)
    }
  }

  const stopRecording = async () => {
    if (recorderRef.current && recorderRef.current.state === 'recording') {
      recorderRef.current.stop()
      // Wait for recording to stop and get the blob
      // The promise will resolve when onstop is called
    }
    setIsRecording(false)
    if (timerRef.current) {
      const finalTime = recordingTime
      setVideoDuration(finalTime)
      clearInterval(timerRef.current)
      timerRef.current = null
    }
    // Stop face detection
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current)
      detectionIntervalRef.current = null
    }
    // Clear canvas
    const canvas = canvasRef.current
    if (canvas) {
      const ctx = canvas.getContext('2d')
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }
    setFacesDetected([])
    setFaceDetectionStatus(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setValidationInfo(null)
    setLoading(true)

    if (!recordedVideo) {
      setError('Please record a video first')
      setLoading(false)
      return
    }

    if (!name.trim()) {
      setError('Please enter a name')
      setLoading(false)
      return
    }

    try {
      const user = await usersAPI.registerWithVideo(
        name.trim(),
        email || undefined,
        employeeId || undefined,
        recordedVideo,
        5, // min_frames_with_face
        0.5 // min_quality_score
      )
      
      setSuccess(`User "${user.name}" registered successfully! (ID: ${user.id})`)
      // Show success info (registration_info is logged but not in response)
      // Just show success message
      setName('')
      setEmail('')
      setEmployeeId('')
      setRecordedVideo(null)
    } catch (err) {
      console.error('Registration error:', err)
      const errorDetail = err.response?.data?.detail
      
      if (errorDetail && typeof errorDetail === 'object' && errorDetail.validation) {
        // Video validation failed
        const validation = errorDetail.validation
        setValidationInfo(validation)
        setError(`Video validation failed: ${errorDetail.message || 'Video does not meet requirements'}`)
      } else {
        const errorMsg = typeof errorDetail === 'string' ? errorDetail : (err.response?.data?.detail?.message || err.message || 'Registration failed')
        setError(errorMsg)
      }
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
              <h3>Face Capture (Video)</h3>
              <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
                Record a 5-7 second video of your face. Look directly at the camera, ensure good lighting, and hold still.
              </p>
              
              <div className="camera-section">
                {!recordedVideo ? (
                  <>
                    <div style={{ position: 'relative', width: '100%', maxWidth: '640px' }}>
                      <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        className="camera-preview"
                        style={{ display: cameraActive ? 'block' : 'none' }}
                      />
                      {/* Canvas overlay for face detection boxes */}
                      <canvas
                        ref={canvasRef}
                        style={{
                          position: 'absolute',
                          top: 0,
                          left: 0,
                          width: '100%',
                          height: '100%',
                          pointerEvents: 'none',
                          zIndex: 10
                        }}
                      />
                      
                      {isRecording && (
                        <>
                          <div style={{
                            position: 'absolute',
                            top: '16px',
                            left: '16px',
                            background: 'rgba(255, 0, 0, 0.8)',
                            color: 'white',
                            padding: '8px 16px',
                            borderRadius: '8px',
                            fontSize: '18px',
                            fontWeight: 'bold',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            zIndex: 20
                          }}>
                            <span style={{
                              width: '12px',
                              height: '12px',
                              background: 'white',
                              borderRadius: '50%',
                              animation: 'blink 1s infinite'
                            }}></span>
                            Recording... {recordingTime.toFixed(1)}s
                          </div>
                          
                          {/* Face Detection Status Indicator */}
                          {faceDetectionStatus === 'detecting' && (
                            <div style={{
                              position: 'absolute',
                              top: '16px',
                              right: '16px',
                              background: 'rgba(255, 165, 0, 0.8)',
                              color: 'white',
                              padding: '8px 16px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: 'bold',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              zIndex: 20
                            }}>
                              <span>🔍</span>
                              Detecting...
                            </div>
                          )}
                          
                          {faceDetectionStatus === 'detected' && facesDetected.length > 0 && (
                            <div style={{
                              position: 'absolute',
                              top: '16px',
                              right: '16px',
                              background: 'rgba(0, 255, 0, 0.8)',
                              color: 'white',
                              padding: '8px 16px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: 'bold',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              zIndex: 20
                            }}>
                              <span>✅</span>
                              Face Detected ({facesDetected.length})
                            </div>
                          )}
                          
                          {faceDetectionStatus === 'none' && (
                            <div style={{
                              position: 'absolute',
                              top: '16px',
                              right: '16px',
                              background: 'rgba(255, 0, 0, 0.8)',
                              color: 'white',
                              padding: '8px 16px',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: 'bold',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              zIndex: 20
                            }}>
                              <span>⚠️</span>
                              No Face Detected
                            </div>
                          )}
                        </>
                      )}
                      
                      {!cameraActive && !isRecording && (
                        <div className="camera-placeholder">
                          <div className="placeholder-icon">🎥</div>
                          <p>Camera not started</p>
                        </div>
                      )}
                    </div>

                    <div className="camera-controls">
                      {!cameraActive ? (
                        <button type="button" onClick={startVideo} className="btn-primary">
                          📹 Start Camera
                        </button>
                      ) : isRecording ? (
                        <button type="button" onClick={stopRecording} className="btn-danger">
                          ⏹ Stop Recording
                        </button>
                      ) : (
                        <>
                          <button type="button" onClick={startRecording} className="btn-primary">
                            🎬 Start Recording
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
                    <div style={{
                      width: '100%',
                      maxWidth: '640px',
                      padding: '16px',
                      background: '#f0f0f0',
                      borderRadius: '12px',
                      textAlign: 'center'
                    }}>
                      <p style={{ margin: '0 0 16px 0', color: '#666' }}>
                        ✅ Video recorded successfully ({videoDuration > 0 ? videoDuration.toFixed(1) : '7.0'}s)
                      </p>
                      <button
                        type="button"
                        onClick={() => {
                          setRecordedVideo(null)
                          setValidationInfo(null)
                          startVideo()
                        }}
                        className="btn-secondary"
                      >
                        🔄 Retake Video
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {validationInfo && (
              <div style={{
                background: '#e3f2fd',
                padding: '16px',
                borderRadius: '8px',
                margin: '16px 0',
                fontSize: '14px'
              }}>
                <h4 style={{ margin: '0 0 8px 0', color: '#1976d2' }}>Validation Results</h4>
                {validationInfo.issues && validationInfo.issues.length > 0 && (
                  <div style={{ marginBottom: '12px' }}>
                    <strong>Issues:</strong>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      {validationInfo.issues.map((issue, idx) => (
                        <li key={idx} style={{ color: '#d32f2f' }}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {validationInfo.recommendations && validationInfo.recommendations.length > 0 && (
                  <div>
                    <strong>Recommendations:</strong>
                    <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                      {validationInfo.recommendations.map((rec, idx) => (
                        <li key={idx} style={{ color: '#388e3c' }}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {validationInfo.frames_analyzed !== undefined && (
                  <div style={{ marginTop: '8px', color: '#666' }}>
                    <div>Frames analyzed: {validationInfo.frames_analyzed}</div>
                    <div>Frames meeting requirements: {validationInfo.frames_meeting_requirements} / {validationInfo.min_frames_required || 5}</div>
                    {validationInfo.best_frame_quality !== undefined && (
                      <div>Best frame quality: {(validationInfo.best_frame_quality * 100).toFixed(1)}%</div>
                    )}
                  </div>
                )}
              </div>
            )}

            {error && <div className="error-message">{error}</div>}
            {success && <div className="success-message">{success}</div>}

            <button type="submit" className="btn-primary btn-submit" disabled={loading || !recordedVideo}>
              {loading ? 'Registering...' : '✅ Register User'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default RegisterUserPage

