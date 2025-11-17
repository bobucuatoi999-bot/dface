import React, { useState, useRef, useEffect } from 'react'
import wsService from '../services/websocket'
import { captureFrame, imageToBase64, startCamera, stopCamera } from '../utils/camera'
import './RecognitionPage.css'

function RecognitionPage() {
  const [isActive, setIsActive] = useState(false)
  const [connected, setConnected] = useState(false)
  const [faces, setFaces] = useState([])
  const [stats, setStats] = useState({ totalFrames: 0, totalFaces: 0 })
  const [liveFeedback, setLiveFeedback] = useState('Position your face inside the circle')
  
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const streamRef = useRef(null)
  const frameIntervalRef = useRef(null)

  useEffect(() => {
    wsService.onFrameResult = handleRecognitionResult
    wsService.onConnectionChange = setConnected

    return () => {
      stopRecognition()
      wsService.disconnect()
    }
  }, [])

  const handleRecognitionResult = (data) => {
    if (data.type === 'recognition_result') {
      setFaces(data.faces || [])
      setStats(prev => ({
        totalFrames: prev.totalFrames + 1,
        totalFaces: Math.max(prev.totalFaces, data.faces?.length || 0)
      }))
      drawBoundingBoxes(data.faces || [])
    }
  }

  const OPTIMAL_FACE_SIZE_MIN = 150
  const OPTIMAL_FACE_SIZE_MAX = 350
  const visualScale = 1.6

  const drawCircleGuide = (ctx, canvasWidth, canvasHeight) => {
    const centerX = canvasWidth / 2
    const centerY = canvasHeight / 2

    const baseInnerRadius = OPTIMAL_FACE_SIZE_MIN / 2
    const baseOuterRadius = OPTIMAL_FACE_SIZE_MAX / 2

    let optimalInnerRadius = baseInnerRadius * visualScale
    let optimalOuterRadius = baseOuterRadius * visualScale

    const maxRadius = Math.min(canvasWidth, canvasHeight) * 0.45
    if (optimalOuterRadius > maxRadius) {
      const scale = maxRadius / optimalOuterRadius
      optimalOuterRadius *= scale
      optimalInnerRadius *= scale
    }

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)'
    ctx.lineWidth = 3
    ctx.setLineDash([8, 4])
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalOuterRadius, 0, 2 * Math.PI)
    ctx.stroke()
    ctx.setLineDash([])

    ctx.strokeStyle = 'rgba(0, 255, 0, 0.4)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalInnerRadius, 0, 2 * Math.PI)
    ctx.stroke()

    ctx.strokeStyle = 'rgba(255, 255, 0, 0.4)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(centerX, centerY, (optimalInnerRadius + optimalOuterRadius) / 2, 0, 2 * Math.PI)
    ctx.stroke()
  }

  const updateLiveFeedback = (message) => {
    setLiveFeedback(prev => (prev === message ? prev : message))
  }

  const drawBoundingBoxes = (detectedFaces) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    const ctx = canvas.getContext('2d')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height

    ctx.clearRect(0, 0, canvasWidth, canvasHeight)
    drawCircleGuide(ctx, canvasWidth, canvasHeight)

    const centerX = canvasWidth / 2
    const centerY = canvasHeight / 2

    let bestFace = null
    let bestScore = -Infinity
    let overlayMessage = 'Position your face inside the circle'
    let overlayStatus = ''
    let overlayDetail = ''

    detectedFaces.forEach((face) => {
      const posStatus = face.position_status || {}
      let score = 0

      if (posStatus.quality_status === 'excellent') score += 3
      else if (posStatus.quality_status === 'good') score += 2
      else if (posStatus.quality_status === 'fair') score += 1

      if (posStatus.distance_status === 'perfect') score += 2
      else if (posStatus.distance_status === 'acceptable') score += 1

      if (!face.is_unknown) score += 0.5
      if (face.confidence) score += face.confidence

      if (score > bestScore) {
        bestScore = score
        bestFace = face
      }
    })

    if (!detectedFaces || detectedFaces.length === 0) {
      overlayMessage = 'No face detected - align your face within the circle'
      updateLiveFeedback(overlayMessage)
      overlayStatus = 'No face detected'
      // no best face info to store
    } else if (bestFace && bestFace.position_status) {
      const distanceStatus = bestFace.position_status.distance_status || 'acceptable'
      const qualityStatus = bestFace.position_status.quality_status || 'fair'
      const positionStatus = bestFace.position_status.position_status || 'centered'

      if (distanceStatus === 'perfect' && positionStatus === 'centered') {
        overlayMessage = '✅ Perfect! Hold still for accurate recognition'
      } else if (distanceStatus === 'too_far') {
        overlayMessage = '⚠️ Move closer to fill the circle'
      } else if (distanceStatus === 'too_close') {
        overlayMessage = '⚠️ Move slightly back'
      } else if (qualityStatus === 'fair') {
        overlayMessage = 'ℹ️ Lighting could be improved, but still acceptable'
      } else if (positionStatus === 'off_center') {
        overlayMessage = '↔ Center your face inside the circle'
      } else {
        overlayMessage = 'Adjust slightly to stay within the circle'
      }

      overlayStatus = `Distance: ${distanceStatus} | Position: ${positionStatus}`
      overlayDetail = `size=${bestFace.position_status.face_size || '?'} | quality=${bestFace.position_status.quality_status || '?'}`
      updateLiveFeedback(overlayMessage)
    } else {
      overlayMessage = 'Face detected - adjusting positioning...'
      overlayStatus = 'Align face with the guide'
      updateLiveFeedback(overlayMessage)
      // keep guidance general when no detailed status
    }

    detectedFaces.forEach((face) => {
      const [top, right, bottom, left] = face.bbox
      const width = right - left
      const height = bottom - top
      const posStatus = face.position_status || {}
      const distanceStatus = posStatus.distance_status || 'acceptable'
      const qualityStatus = posStatus.quality_status || 'fair'

      let color = '#ff4444'
      if (distanceStatus === 'perfect' && qualityStatus !== 'poor') {
        color = '#00ff88'
      } else if (distanceStatus === 'acceptable') {
        color = '#ffaa00'
      } else if (!face.is_unknown && face.confidence > 0.85) {
        color = '#44ff44'
      } else if (!face.is_unknown) {
        color = '#ffaa00'
      }

      ctx.strokeStyle = color
      ctx.lineWidth = 3
      ctx.strokeRect(left, top, width, height)

      // Draw face landmarks if available (from WebSocket recognition result)
      // Note: WebSocket might not send landmarks, but we can try
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

      const labelText = face.is_unknown
        ? 'Unknown'
        : `${face.user_name} (${(face.confidence * 100).toFixed(0)}%)`
      
      ctx.fillStyle = color
      ctx.fillRect(left, top - 30, Math.max(150, labelText.length * 8), 30)

      ctx.fillStyle = 'white'
      ctx.font = 'bold 16px sans-serif'
      ctx.fillText(labelText, left + 5, top - 8)

      if (posStatus && posStatus.distance_status) {
        const diagnostic = `size=${posStatus.face_size || '?'} dist=${posStatus.distance_status} quality=${posStatus.quality_status}`
        ctx.font = '12px monospace'
        ctx.fillStyle = '#ffffff'
        ctx.fillText(diagnostic, left + 5, top + height + 18)
      }
    })

    // Draw live feedback overlay inside circle
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)'
    ctx.fillRect(centerX - 230, centerY - 75, 460, 150)

    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 20px sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'

    ctx.fillText(overlayMessage || 'Position your face in the circle', centerX, centerY - 20)

    ctx.font = '16px sans-serif'
    ctx.fillText(overlayStatus || (detectedFaces && detectedFaces.length > 0 ? 'Align face with the guide' : 'No face detected'), centerX, centerY + 5)

    ctx.font = '14px sans-serif'
    ctx.fillStyle = '#dddddd'
    ctx.fillText(overlayDetail || 'Tip: Keep your face steady inside the circle', centerX, centerY + 28)
  }

  const startRecognition = async () => {
    try {
      // Start camera
      const stream = await startCamera(videoRef.current)
      streamRef.current = stream

      // Connect WebSocket
      await wsService.connect()
      setConnected(true)

      setIsActive(true)

      // Start sending frames (5 FPS)
      let frameId = 0
      frameIntervalRef.current = setInterval(async () => {
        if (videoRef.current && videoRef.current.readyState === 4) {
          try {
            // Capture frame optimized for detection (smaller size, faster processing)
            const imageData = await captureFrame(videoRef.current, {
              forDetection: true,  // Optimize for detection
              maxSize: 960,  // Resize to max 960px for faster processing
              quality: 0.85  // Lower JPEG quality for faster upload/processing
            })
            const base64Image = imageToBase64(imageData)
            wsService.sendFrame(base64Image, frameId++, Date.now())
          } catch (error) {
            console.error('Error capturing frame:', error)
          }
        }
      }, 200) // 5 FPS = 200ms per frame
    } catch (error) {
      console.error('Error starting recognition:', error)
      alert('Failed to start recognition. Check camera permissions.')
    }
  }

  const stopRecognition = () => {
    setIsActive(false)
    
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current)
      frameIntervalRef.current = null
    }

    if (streamRef.current) {
      stopCamera(streamRef.current)
      streamRef.current = null
    }

    wsService.disconnect()
    setConnected(false)
    setFaces([])
  }

  return (
    <div className="recognition-page">
      <h1 className="page-title">🎥 Recognition Mode</h1>
      <p className="page-subtitle">Real-time face recognition from camera</p>

      <div className="recognition-container">
        <div className="video-section">
          {isActive && (
            <div className="position-guide-info">
              <p className="guide-text">
                {liveFeedback || '📍 Position your face within the white circle guide for best recognition'}
              </p>
            </div>
          )}
          <div className="video-wrapper">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="recognition-video"
              style={{ display: isActive ? 'block' : 'none' }}
            />
            <canvas ref={canvasRef} className="recognition-canvas" />
            {!isActive && (
              <div className="video-placeholder">
                <div className="placeholder-icon">🎬</div>
                <p>Click "Start Recognition" to begin</p>
              </div>
            )}
          </div>

          <div className="recognition-controls">
            {!isActive ? (
              <button onClick={startRecognition} className="btn-primary btn-large">
                ▶ Start Recognition
              </button>
            ) : (
              <button onClick={stopRecognition} className="btn-danger btn-large">
                ⏹ Stop Recognition
              </button>
            )}
          </div>
        </div>

        <div className="recognition-sidebar">
          <div className="status-card">
            <h3>Status</h3>
            <div className="status-item">
              <span className="status-label">Connection:</span>
              <span className={`status-value ${connected ? 'connected' : 'disconnected'}`}>
                {connected ? '🟢 Connected' : '🔴 Disconnected'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Active:</span>
              <span className={`status-value ${isActive ? 'active' : 'inactive'}`}>
                {isActive ? '🟢 Active' : '⚪ Inactive'}
              </span>
            </div>
            <div className="status-item">
              <span className="status-label">Faces Detected:</span>
              <span className="status-value">{faces.length}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Frames Processed:</span>
              <span className="status-value">{stats.totalFrames}</span>
            </div>
          </div>

          <div className="faces-card">
            <h3>Detected Faces</h3>
            {faces.length === 0 ? (
              <p className="no-faces">No faces detected</p>
            ) : (
              <div className="faces-list">
                {faces.map((face, index) => (
                  <div
                    key={face.track_id || index}
                    className={`face-item ${face.is_unknown ? 'unknown' : 'recognized'}`}
                  >
                    <div className="face-header">
                      <span className="face-track">Track #{face.track_id}</span>
                      {face.is_unknown ? (
                        <span className="face-badge unknown-badge">Unknown</span>
                      ) : (
                        <span className="face-badge recognized-badge">
                          {(face.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </div>
                    {!face.is_unknown && (
                      <div className="face-name">{face.user_name}</div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default RecognitionPage

