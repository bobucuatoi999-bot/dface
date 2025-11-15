import React, { useState, useRef, useEffect } from 'react'
import wsService from '../services/websocket'
import { captureFrame, imageToBase64, startCamera, stopCamera } from '../utils/camera'
import './RecognitionPage.css'

function RecognitionPage() {
  const [isActive, setIsActive] = useState(false)
  const [connected, setConnected] = useState(false)
  const [faces, setFaces] = useState([])
  const [stats, setStats] = useState({ totalFrames: 0, totalFaces: 0 })
  
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

  const drawBoundingBoxes = (detectedFaces) => {
    const canvas = canvasRef.current
    const video = videoRef.current
    if (!canvas || !video) return

    const ctx = canvas.getContext('2d')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const canvasWidth = canvas.width
    const canvasHeight = canvas.height

    // Clear canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight)

    // Draw optimal position guide circle (centered)
    const centerX = canvasWidth / 2
    const centerY = canvasHeight / 2
    
    // Calculate optimal circle size based on optimal face size range
    // Optimal face size: 150-350px, assume face takes ~40% of circle diameter
    const optimalCircleRadius = 350 / 0.4 / 2 // ~437px radius
    
    // Draw guide circle (always visible)
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)' // Semi-transparent white
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5]) // Dashed line
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalCircleRadius, 0, 2 * Math.PI)
    ctx.stroke()
    ctx.setLineDash([]) // Reset line style
    
    // Draw inner circle (optimal zone)
    ctx.strokeStyle = 'rgba(0, 255, 0, 0.3)' // Green, very transparent
    ctx.lineWidth = 1
    const optimalInnerRadius = 150 / 0.4 / 2 // ~187px radius
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalInnerRadius, 0, 2 * Math.PI)
    ctx.stroke()
    
    // Draw outer circle (max acceptable zone)
    ctx.strokeStyle = 'rgba(255, 255, 0, 0.3)' // Yellow, very transparent
    ctx.lineWidth = 1
    const optimalOuterRadius = optimalCircleRadius * 1.2
    ctx.beginPath()
    ctx.arc(centerX, centerY, optimalOuterRadius, 0, 2 * Math.PI)
    ctx.stroke()

    // Draw bounding boxes with landmarks if available
    detectedFaces.forEach((face) => {
      const [top, right, bottom, left] = face.bbox
      const width = right - left
      const height = bottom - top

      // Choose color based on recognition status
      let color = '#ff4444' // Red for unknown
      if (!face.is_unknown && face.confidence > 0.85) {
        color = '#44ff44' // Green for recognized
      } else if (!face.is_unknown) {
        color = '#ffaa00' // Yellow for uncertain
      }

      // Draw bounding box
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

      // Draw label background
      const labelText = face.is_unknown
        ? 'Unknown'
        : `${face.user_name} (${(face.confidence * 100).toFixed(0)}%)`
      
      ctx.fillStyle = color
      ctx.fillRect(left, top - 30, Math.max(150, labelText.length * 8), 30)

      // Draw label text
      ctx.fillStyle = 'white'
      ctx.font = 'bold 16px sans-serif'
      ctx.fillText(labelText, left + 5, top - 8)
    })
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
            const imageData = await captureFrame(videoRef.current)
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
                📍 Position your face within the white circle guide for best recognition
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

