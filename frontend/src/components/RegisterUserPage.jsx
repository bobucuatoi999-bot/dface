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
  const [meetsRequirements, setMeetsRequirements] = useState(false) // Track if face meets quality requirements
  const [liveFeedback, setLiveFeedback] = useState('') // Live feedback text shown in circle
  const requirementsMetRef = useRef(false) // Track best status during recording
  
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

  // Draw circle guide (always visible when camera is active)
  const drawCircleGuide = () => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video || !video.videoWidth || !video.videoHeight) return
    
    const ctx = canvas.getContext('2d')
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height
    
    const centerX = canvasWidth / 2
    const centerY = canvasHeight / 2
    
    // Calculate optimal circle size based on optimal face size range
    // Optimal face size: 150-350px, assume face takes ~40% of circle diameter
    const optimalCircleRadius = 350 / 0.4 / 2 // ~437px radius
    
    // Draw guide circle (always visible when camera is active)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)' // More visible white
    ctx.lineWidth = 3
    ctx.setLineDash([8, 4]) // Dashed line
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalCircleRadius, 0, 2 * Math.PI)
    ctx.stroke()
    ctx.setLineDash([]) // Reset line style
    
    // Draw inner circle (optimal zone)
    ctx.strokeStyle = 'rgba(0, 255, 0, 0.4)' // Green, more visible
    ctx.lineWidth = 2
    const optimalInnerRadius = 150 / 0.4 / 2 // ~187px radius
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalInnerRadius, 0, 2 * Math.PI)
    ctx.stroke()
    
    // Draw outer circle (max acceptable zone)
    ctx.strokeStyle = 'rgba(255, 255, 0, 0.4)' // Yellow, more visible
    ctx.lineWidth = 2
    const optimalOuterRadius = optimalCircleRadius * 1.2
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalOuterRadius, 0, 2 * Math.PI)
    ctx.stroke()
  }

  // Draw face detection boxes, landmarks, and optimal position guide
  const drawFaceBoxes = (faces, imageSize) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video || !video.videoWidth || !video.videoHeight) return
    
    const ctx = canvas.getContext('2d')
    
    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height
    
    // Clear canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    
    // Always draw circle guide when camera is active
    if (cameraActive) {
      drawCircleGuide()
    }
    
    // Draw optimal position guide circle center for reference
    const centerX = canvasWidth / 2
    const centerY = canvasHeight / 2
    
    // Draw live feedback text inside/near circle (when camera is active, not just recording)
    if (cameraActive) {
      // Background for text readability
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
      ctx.fillRect(centerX - 200, centerY - 60, 400, 120)
      
      // Text styling
      ctx.fillStyle = '#ffffff'
      ctx.font = 'bold 20px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // Draw main feedback message
      let feedbackText = liveFeedback || 'Position your face in the circle'
      let feedbackColor = '#ffffff'
      
      if (meetsRequirements) {
        feedbackText = '✅ Perfect! Keep your position'
        feedbackColor = '#00ff00'
      } else if (liveFeedback) {
        if (liveFeedback.includes('Too Far')) {
          feedbackColor = '#ffaa00' // Orange
        } else if (liveFeedback.includes('Too Close')) {
          feedbackColor = '#ffaa00' // Orange
        } else if (liveFeedback.includes('No face')) {
          feedbackColor = '#ff4444' // Red
        }
      }
      
      ctx.fillStyle = feedbackColor
      ctx.fillText(feedbackText, centerX, centerY - 15)
      
      // Draw status text below
      ctx.font = '16px sans-serif'
      ctx.fillStyle = '#ffffff'
      let statusText = ''
      if (isRecording) {
        statusText = meetsRequirements 
          ? 'Requirements met - Recording...' 
          : 'Adjust position to meet requirements'
      } else {
        statusText = 'Position face in center - Ready to record'
      }
      ctx.fillText(statusText, centerX, centerY + 15)
      
      // Draw requirement status
      ctx.font = '14px sans-serif'
      ctx.fillStyle = meetsRequirements ? '#00ff00' : '#ffaa00'
      let requirementStatus = ''
      if (isRecording) {
        requirementStatus = meetsRequirements
          ? '✓ Ready to submit'
          : '✗ Requirements not met'
      } else {
        requirementStatus = meetsRequirements
          ? '✓ Ready to record'
          : 'Adjust position before recording'
      }
      ctx.fillText(requirementStatus, centerX, centerY + 40)
    }
    
    if (faces && faces.length > 0) {
      let bestFace = null
      let bestQuality = 0
      
      // Find the best quality face
      faces.forEach((face) => {
        const quality = face.quality_score || 0
        const posStatus = face.position_status || {}
        const qualityStatus = posStatus.quality_status || 'poor'
        
        // Score face quality
        let score = quality
        if (qualityStatus === 'excellent') score += 0.3
        else if (qualityStatus === 'good') score += 0.2
        else if (qualityStatus === 'fair') score += 0.1
        
        if (score > bestQuality) {
          bestQuality = score
          bestFace = face
        }
      })
      
      if (bestFace) {
        const face = bestFace
        const [top, right, bottom, left] = face.bbox
        const width = right - left
        const height = bottom - top
        const posStatus = face.position_status || {}
        const distanceStatus = posStatus.distance_status || 'acceptable'
        const qualityStatus = posStatus.quality_status || 'fair'
        const sizeStatus = posStatus.size_status || 'acceptable'
        
        // Check if requirements are met (for submit button)
        // Requirements: quality_status must be 'excellent' or 'good', distance_status must be 'perfect'
        const currentMeetsRequirements = (
          (qualityStatus === 'excellent' || qualityStatus === 'good') &&
          distanceStatus === 'perfect'
        )
        
        // Update requirements status (keep best status during recording)
        if (currentMeetsRequirements) {
          requirementsMetRef.current = true
          setMeetsRequirements(true)
        } else if (!requirementsMetRef.current) {
          // Only update to false if we haven't met requirements yet
          setMeetsRequirements(false)
        }
        
        // Choose color based on quality
        let boxColor = '#ff4444' // Red - poor
        let labelBg = '#ff4444'
        
        if (qualityStatus === 'excellent') {
          boxColor = '#00ff00' // Green - excellent
          labelBg = '#00ff00'
        } else if (qualityStatus === 'good') {
          boxColor = '#44ff44' // Light green - good
          labelBg = '#44ff44'
        } else if (qualityStatus === 'fair') {
          boxColor = '#ffaa00' // Orange - fair
          labelBg = '#ffaa00'
        }
        
        // Update live feedback based on current status (always when camera is active)
        if (currentMeetsRequirements) {
          setLiveFeedback(isRecording ? '✅ Perfect Position!' : '✅ Perfect Position - Ready!')
        } else if (distanceStatus === 'too_far') {
          setLiveFeedback('⚠️ Too Far - Move Closer')
        } else if (distanceStatus === 'too_close') {
          setLiveFeedback('⚠️ Too Close - Move Away')
        } else if (qualityStatus === 'fair') {
          setLiveFeedback('⚠️ Quality Fair - Improve Lighting')
        } else if (qualityStatus === 'poor') {
          setLiveFeedback('⚠️ Poor Quality - Better Lighting Needed')
        } else {
          setLiveFeedback('Position face in center')
        }
        
        // Draw bounding box
        ctx.strokeStyle = boxColor
        ctx.lineWidth = 3
        ctx.strokeRect(left, top, width, height)
        
        // Draw face landmarks if available
        if (face.landmarks) {
          const landmarks = face.landmarks
          ctx.strokeStyle = '#00ffff' // Cyan for landmarks
          ctx.lineWidth = 2
          ctx.fillStyle = '#00ffff'
          
          // Draw each landmark feature
          const landmarkFeatures = [
            'chin', 'left_eyebrow', 'right_eyebrow', 'nose_bridge', 
            'nose_tip', 'left_eye', 'right_eye', 'top_lip', 'bottom_lip'
          ]
          
          landmarkFeatures.forEach(feature => {
            if (landmarks[feature] && Array.isArray(landmarks[feature])) {
              ctx.beginPath()
              landmarks[feature].forEach((point, idx) => {
                const [x, y] = point
                if (idx === 0) {
                  ctx.moveTo(x, y)
                } else {
                  ctx.lineTo(x, y)
                }
              })
              ctx.stroke()
              
              // Draw points
              landmarks[feature].forEach((point) => {
                const [x, y] = point
                ctx.beginPath()
                ctx.arc(x, y, 2, 0, 2 * Math.PI)
                ctx.fill()
              })
            }
          })
        }
        
        // Draw label background
        const labelText = `Face Detected - ${distanceStatus === 'perfect' ? 'Perfect' : 
          distanceStatus === 'too_far' ? 'Too Far' :
          distanceStatus === 'too_close' ? 'Too Close' : 'OK'}`
        ctx.fillStyle = labelBg
        ctx.fillRect(left, top - 30, Math.max(250, labelText.length * 7), 30)
        
        // Draw label text
        ctx.fillStyle = 'white'
        ctx.font = 'bold 14px sans-serif'
        ctx.fillText(labelText, left + 5, top - 10)
        
        // Update status
        if (qualityStatus === 'excellent' || qualityStatus === 'good') {
          setFaceDetectionStatus('detected')
        } else if (qualityStatus === 'fair') {
          setFaceDetectionStatus('fair')
        } else {
          setFaceDetectionStatus('poor')
        }
        
        // Update distance feedback message
        if (distanceStatus === 'too_far') {
          setError('⚠️ Too Far - Move closer to the camera')
        } else if (distanceStatus === 'too_close') {
          setError('⚠️ Too Close - Move further from the camera')
        } else if (distanceStatus === 'perfect') {
          setError('') // Clear error
        } else {
          setError('') // Clear error
        }
      }
    } else {
      setFaceDetectionStatus('none')
      // Always update live feedback when camera is active (not just recording)
      if (cameraActive) {
        setLiveFeedback('⚠️ No Face Detected - Position face in center')
        setMeetsRequirements(false)
        requirementsMetRef.current = false
        // Still draw circle guide even if no face
        drawCircleGuide()
      } else {
        setError('⚠️ No face detected - Position your face in the center')
      }
    }
  }

  // Detect faces in video frame (works when camera is active, not just recording)
  const detectFacesInFrame = async () => {
    if (!videoRef.current || !cameraActive) return
    
    try {
      // Capture frame
      const imageData = await captureFrame(videoRef.current)
      const base64Image = imageToBase64(imageData)
      
      // Call enhanced face detection API (now returns landmarks and position status)
      const result = await usersAPI.detectFaces(base64Image)
      
      if (result && result.faces) {
        setFacesDetected(result.faces)
        drawFaceBoxes(result.faces, result.image_size || null)
      } else {
        setFacesDetected([])
        drawFaceBoxes([], null)
      }
    } catch (error) {
      // Silently handle errors
      console.error('Face detection error:', error)
      setFaceDetectionStatus(null)
      // Still draw circle guide even if detection fails
      if (cameraActive) {
        drawCircleGuide()
      }
    }
  }

  const startVideo = async () => {
    try {
      setError('')
      const stream = await startCamera(videoRef.current)
      streamRef.current = stream
      setCameraActive(true)
      
      // Wait for video to be ready, then draw circle guide
      const checkVideoReady = () => {
        if (videoRef.current && videoRef.current.readyState >= 2) {
          // Draw circle guide immediately when camera starts
          setTimeout(() => {
            drawCircleGuide()
            setLiveFeedback('Position your face in the circle guide')
          }, 100)
        } else {
          setTimeout(checkVideoReady, 100)
        }
      }
      checkVideoReady()
      
      // Start continuous face detection when camera is active (even before recording)
      // This allows users to see feedback and position correctly before recording
      setFaceDetectionStatus('detecting')
      detectionIntervalRef.current = setInterval(() => {
        detectFacesInFrame()
      }, 500) // Check every 500ms (2 FPS) when not recording - less frequent to save resources
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
      
      // Validate video element and stream before starting
      if (!videoRef.current) {
        setError('Video element is not available')
        return
      }
      
      if (!videoRef.current.srcObject) {
        setError('Camera is not started. Please start the camera first.')
        return
      }
      
      const stream = videoRef.current.srcObject
      const videoTracks = stream.getVideoTracks()
      if (videoTracks.length === 0 || videoTracks[0].readyState !== 'live') {
        setError('Camera is not ready. Please wait a moment and try again.')
        return
      }
      
      setIsRecording(true)
      setRecordingTime(0)
      setVideoDuration(0)
      setMeetsRequirements(false) // Reset requirements status
      requirementsMetRef.current = false // Reset requirements ref
      setLiveFeedback('Detecting face...') // Initial feedback

      // Start video recording (7 seconds duration)
      // startVideoRecording now returns a Promise, so we need to await it
      const result = await startVideoRecording(videoRef.current, {
        duration: 7000,
        mimeType: 'video/webm;codecs=vp8,opus'
      })
      
      const { recorder, promise } = result
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

      // Increase face detection frequency during recording (every 300ms = ~3 FPS)
      // If detection interval already exists (from camera start), clear it and restart with faster rate
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current)
      }
      setFaceDetectionStatus('detecting')
      detectionIntervalRef.current = setInterval(() => {
        detectFacesInFrame()
      }, 300) // Faster detection during recording

      // Wait for recording to complete (will auto-stop at 7 seconds)
      const videoBlob = await promise
      
      // Clear timer
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
      
      // Keep face detection running after recording (for preview with circle guide)
      // Don't stop detection interval - it will continue showing feedback
      // Only stop when camera is stopped
      
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
      
      // Check if requirements were met during recording
      if (!requirementsMetRef.current) {
        setError('⚠️ Video does not meet quality requirements. Please record again with your face in the optimal position (within the circle guide).')
        setRecordedVideo(null) // Clear video so user can record again
        setMeetsRequirements(false)
      } else {
        setError('') // Clear any errors if requirements met
      }
      
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
                    {cameraActive && (
                      <div className="position-guide-info">
                        <p className="guide-text">
                          📍 Position your face within the white circle guide for best recognition
                        </p>
                      </div>
                    )}
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

            <button 
              type="submit" 
              className="btn-primary btn-submit" 
              disabled={loading || !recordedVideo || !meetsRequirements}
              title={!recordedVideo ? 'Please record a video first' : !meetsRequirements ? 'Video does not meet quality requirements. Please record again with your face in the optimal position.' : ''}
            >
              {loading ? 'Registering...' : '✅ Register User'}
            </button>
            {!meetsRequirements && recordedVideo && (
              <p style={{ color: '#ff4444', fontSize: '14px', marginTop: '8px', textAlign: 'center' }}>
                ⚠️ Video does not meet quality requirements. Please record again with your face positioned within the circle guide.
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}

export default RegisterUserPage

