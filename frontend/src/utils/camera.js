/**
 * Camera utilities for capturing images
 */

export const captureImageFromVideo = (videoElement) => {
  const canvas = document.createElement('canvas')
  canvas.width = videoElement.videoWidth
  canvas.height = videoElement.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(videoElement, 0, 0)
  return canvas.toDataURL('image/jpeg', 0.8)
}

export const imageToBase64 = (imageDataUrl) => {
  // Remove data URL prefix if present
  if (imageDataUrl.includes(',')) {
    return imageDataUrl.split(',')[1]
  }
  return imageDataUrl
}

export const startCamera = async (videoElement, constraints = {}) => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 },
        ...constraints
      }
    })
    videoElement.srcObject = stream
    return stream
  } catch (error) {
    console.error('Error accessing camera:', error)
    throw error
  }
}

export const stopCamera = (stream) => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
  }
}

export const captureFrame = (videoElement, options = {}) => {
  return new Promise((resolve, reject) => {
    try {
      const {
        forDetection = false,  // If true, optimize for faster detection
        maxSize = null,  // Maximum size for detection frames (default: 960px)
        quality = null  // JPEG quality (default: 0.95 for registration, 0.85 for detection)
      } = options

      // Validate video element
      if (!videoElement) {
        reject(new Error('Video element is not available'))
        return
      }

      // Get actual video dimensions (not scaled display size)
      const videoWidth = videoElement.videoWidth || videoElement.clientWidth || 640
      const videoHeight = videoElement.videoHeight || videoElement.clientHeight || 480

      // Validate dimensions
      if (videoWidth === 0 || videoHeight === 0) {
        console.warn('Video dimensions are 0, using fallback dimensions')
        reject(new Error('Video is not ready - dimensions are 0'))
        return
      }

      // Check if video is playing/ready
      if (videoElement.readyState < 2) { // HAVE_CURRENT_DATA
        console.warn('Video not ready, readyState:', videoElement.readyState)
        reject(new Error('Video is not ready'))
        return
      }

      // For detection: resize to smaller size for faster processing
      // For registration: use full resolution
      let canvasWidth = videoWidth
      let canvasHeight = videoHeight
      
      if (forDetection && maxSize) {
        const maxDim = Math.max(videoWidth, videoHeight)
        if (maxDim > maxSize) {
          const scale = maxSize / maxDim
          canvasWidth = Math.round(videoWidth * scale)
          canvasHeight = Math.round(videoHeight * scale)
        }
      }

      // Create canvas with optimized dimensions
      const canvas = document.createElement('canvas')
      canvas.width = canvasWidth
      canvas.height = canvasHeight

      const ctx = canvas.getContext('2d', {
        alpha: false,  // Disable alpha for better performance
        desynchronized: true,  // Allow async rendering for better performance
        willReadFrequently: false  // We're not reading frequently
      })

      // Use high-quality image settings
      ctx.imageSmoothingEnabled = true
      ctx.imageSmoothingQuality = forDetection ? 'medium' : 'high'  // Medium quality for faster detection

      // Draw video frame to canvas (scaled if needed)
      ctx.drawImage(videoElement, 0, 0, canvasWidth, canvasHeight)

      // Choose JPEG quality: lower for detection (faster), higher for registration (better quality)
      const jpegQuality = quality !== null ? quality : (forDetection ? 0.85 : 0.95)

      // Convert to JPEG
      const imageData = canvas.toDataURL('image/jpeg', jpegQuality)
      
      if (!imageData || imageData.length < 100) {
        reject(new Error('Failed to capture frame - image data is too small'))
        return
      }

      // Log frame capture for debugging
      console.debug(`Frame captured: ${canvasWidth}x${canvasHeight} (from ${videoWidth}x${videoHeight}), ` +
                   `quality=${jpegQuality}, forDetection=${forDetection}, data length=${imageData.length}`)

      resolve(imageToBase64(imageData))
    } catch (error) {
      console.error('Error capturing frame:', error)
      reject(error)
    }
  })
}

// Video recording utilities
export const startVideoRecording = (videoElement, options = {}) => {
  const {
    duration = 7000, // 7 seconds default
    mimeType = 'video/webm;codecs=vp8,opus'
  } = options

  return new Promise((resolve, reject) => {
    // First, ensure video element is ready
    const checkVideoReady = () => {
      return new Promise((resolveCheck) => {
        if (!videoElement) {
          reject(new Error('Video element is not available'))
          return
        }

        const stream = videoElement.srcObject
        if (!stream) {
          reject(new Error('No video stream available. Please start the camera first.'))
          return
        }

        // Check if stream has active tracks
        const videoTracks = stream.getVideoTracks()
        const audioTracks = stream.getAudioTracks()
        
        if (videoTracks.length === 0) {
          reject(new Error('No video tracks in stream. Please check your camera.'))
          return
        }

        const activeVideoTrack = videoTracks.find(track => track.readyState === 'live')
        if (!activeVideoTrack) {
          reject(new Error('Video track is not active. Please wait for camera to initialize.'))
          return
        }

        // Wait for video element to be playing (if it's a video element)
        if (videoElement.tagName === 'VIDEO') {
          if (videoElement.readyState >= 2) { // HAVE_CURRENT_DATA or higher
            console.log('Video element is ready, readyState:', videoElement.readyState)
            resolveCheck()
          } else {
            const onCanPlay = () => {
              console.log('Video element can play now')
              videoElement.removeEventListener('canplay', onCanPlay)
              resolveCheck()
            }
            videoElement.addEventListener('canplay', onCanPlay)
            
            // Timeout after 3 seconds
            setTimeout(() => {
              videoElement.removeEventListener('canplay', onCanPlay)
              console.warn('Video ready check timeout, proceeding anyway')
              resolveCheck()
            }, 3000)
          }
        } else {
          resolveCheck()
        }
      })
    }

    checkVideoReady().then(() => {
      try {
        const stream = videoElement.srcObject

        // Check if MediaRecorder supports the requested mimeType
        const supportedTypes = [
          'video/webm;codecs=vp8,opus',
          'video/webm;codecs=vp9,opus',
          'video/webm;codecs=h264,opus',
          'video/webm',
          'video/mp4'
        ]
        
        let selectedMimeType = mimeType
        let isSupported = MediaRecorder.isTypeSupported(mimeType)
        
        if (!isSupported) {
          console.warn(`MIME type ${mimeType} not supported, trying alternatives...`)
          for (const type of supportedTypes) {
            if (MediaRecorder.isTypeSupported(type)) {
              selectedMimeType = type
              isSupported = true
              console.log(`Using alternative MIME type: ${type}`)
              break
            }
          }
        }
        
        if (!isSupported) {
          throw new Error('No supported video format found. Please use a modern browser.')
        }

        const mediaRecorder = new MediaRecorder(stream, { 
          mimeType: selectedMimeType,
          videoBitsPerSecond: 2500000 // 2.5 Mbps for better quality
        })
        const chunks = []

        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            chunks.push(event.data)
            console.log(`Received chunk: ${event.data.size} bytes (total: ${chunks.length} chunks, ${chunks.reduce((sum, c) => sum + c.size, 0)} bytes)`)
          } else {
            console.warn('Received empty chunk')
          }
        }

        const promise = new Promise((resolveRecord, rejectRecord) => {
          let hasStopped = false
          
          const timeout = setTimeout(() => {
            if (mediaRecorder.state === 'recording') {
              console.log('Auto-stopping recording after', duration, 'ms')
              mediaRecorder.stop()
            }
          }, duration)

          mediaRecorder.onstop = () => {
            if (hasStopped) {
              console.warn('onstop called multiple times')
              return
            }
            hasStopped = true
            clearTimeout(timeout)
            
            console.log(`Recording stopped. State: ${mediaRecorder.state}, Chunks: ${chunks.length}`)
            
            // Request any remaining data
            if (mediaRecorder.state !== 'inactive') {
              mediaRecorder.requestData()
            }
            
            // Give a small delay for any final data events
            setTimeout(() => {
              // Validate chunks
              if (chunks.length === 0) {
                rejectRecord(new Error('No video data recorded. Please try again and ensure your camera is working.'))
                return
              }

              const totalSize = chunks.reduce((sum, chunk) => sum + chunk.size, 0)
              console.log(`Recording complete. Total chunks: ${chunks.length}, Total size: ${totalSize} bytes`)
              
              // Validate minimum size (at least 5KB for a valid 7-second video)
              if (totalSize < 5120) {
                rejectRecord(new Error(`Video file is too small (${totalSize} bytes). Recording may have failed. Please check your camera and try again.`))
                return
              }

              // Create blob and validate immediately
              const blob = new Blob(chunks, { type: selectedMimeType })
              
              console.log(`Creating blob from ${chunks.length} chunks...`)
              console.log(`Chunk sizes:`, chunks.map(c => c.size))
              console.log(`Total chunks size: ${totalSize} bytes`)
              console.log(`Blob size: ${blob.size} bytes`)
              console.log(`Blob type: ${blob.type}`)
              
              // Additional validation: check blob size matches
              if (blob.size !== totalSize) {
                console.warn(`Blob size mismatch: expected ${totalSize}, got ${blob.size}`)
                // If size mismatch is significant, reject
                if (Math.abs(blob.size - totalSize) > 100) {
                  rejectRecord(new Error(`Blob size mismatch: expected ${totalSize} bytes, got ${blob.size} bytes. Recording may have failed.`))
                  return
                }
              }

              // Validate blob is not empty
              if (blob.size === 0) {
                rejectRecord(new Error('Video blob is empty. Recording may have failed.'))
                return
              }
              
              // Validate blob type
              if (!blob.type || !blob.type.startsWith('video/')) {
                console.warn(`Unexpected blob type: ${blob.type}, expected video/*`)
              }
              
              // Validate minimum size again (safety check)
              if (blob.size < 5120) {
                rejectRecord(new Error(`Video blob is too small (${blob.size} bytes). Minimum 5KB required for a 7-second video.`))
                return
              }

              console.log(`✅ Video recorded successfully: ${blob.size} bytes, type: ${selectedMimeType}`)
              resolveRecord(blob)
            }, 200)
          }

          mediaRecorder.onerror = (error) => {
            clearTimeout(timeout)
            console.error('MediaRecorder error:', error)
            rejectRecord(new Error(`Recording error: ${error.error?.message || error.name || 'Unknown error'}`))
          }

          // Start recording with timeslice to ensure data is available
          // Timeslice of 100ms means ondataavailable fires every 100ms
          try {
            mediaRecorder.start(100)
            console.log(`Started recording with MIME type: ${selectedMimeType}, state: ${mediaRecorder.state}`)
            
            // Verify recording actually started
            setTimeout(() => {
              if (mediaRecorder.state === 'recording') {
                console.log('✅ Recording confirmed active')
                
                // Check if chunks are being received
                if (chunks.length === 0) {
                  console.warn('⚠️ No chunks received after 500ms. This might indicate a recording issue.')
                  // Don't reject yet, as chunks might arrive later with timeslice
                } else {
                  const currentSize = chunks.reduce((sum, c) => sum + c.size, 0)
                  console.log(`✅ ${chunks.length} chunks received so far (${currentSize} bytes)`)
                }
              } else {
                console.error('❌ Recording failed to start. State:', mediaRecorder.state)
                rejectRecord(new Error(`Recording failed to start. State: ${mediaRecorder.state}`))
              }
            }, 500)
          } catch (startError) {
            clearTimeout(timeout)
            console.error('Error starting MediaRecorder:', startError)
            rejectRecord(new Error(`Failed to start recording: ${startError.message || 'Unknown error'}`))
          }
        })

        resolve({ recorder: mediaRecorder, promise, mimeType: selectedMimeType })
      } catch (error) {
        console.error('Error setting up video recording:', error)
        reject(error)
      }
    }).catch(reject)
  })
}

export const videoBlobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    // Validate blob first
    if (!blob || !(blob instanceof Blob)) {
      reject(new Error('Invalid blob provided'))
      return
    }

    if (blob.size === 0) {
      reject(new Error('Video blob is empty'))
      return
    }

    if (blob.size < 1024) {
      reject(new Error(`Video blob is too small (${blob.size} bytes). Minimum 1KB required.`))
      return
    }

    console.log(`Converting video blob to base64: ${blob.size} bytes, type: ${blob.type}`)

    // Use ArrayBuffer instead of DataURL for more reliable conversion
    const reader = new FileReader()
    reader.onloadend = () => {
      try {
        const arrayBuffer = reader.result
        
        if (!arrayBuffer || arrayBuffer.byteLength === 0) {
          reject(new Error('Failed to read video blob: ArrayBuffer is empty'))
          return
        }
        
        console.log(`Read ArrayBuffer: ${arrayBuffer.byteLength} bytes`)
        
        // Convert ArrayBuffer to base64
        const bytes = new Uint8Array(arrayBuffer)
        let binary = ''
        for (let i = 0; i < bytes.byteLength; i++) {
          binary += String.fromCharCode(bytes[i])
        }
        
        // Encode to base64
        const base64 = btoa(binary)
        
        console.log(`Base64 encoded: ${base64.length} characters`)
        
        // Validate base64 string length (should be at least 1KB in base64 = ~750 bytes)
        // Base64 is ~33% larger than original binary, so 1KB blob = ~1.3KB base64
        const expectedMinLength = Math.floor(blob.size * 1.3)
        if (base64.length < Math.min(1000, expectedMinLength)) {
          console.error(`Base64 string too short: ${base64.length} chars (expected at least ${Math.min(1000, expectedMinLength)}).`)
          console.error(`Blob size: ${blob.size} bytes, type: ${blob.type}`)
          console.error(`First 100 chars of base64: ${base64.substring(0, 100)}`)
          reject(new Error(`Base64 string too short (${base64.length} chars). Video may be corrupted or recording failed.`))
          return
        }

        console.log(`✅ Base64 conversion successful: ${base64.length} characters`)
        resolve(base64)
      } catch (error) {
        console.error('Error processing base64 string:', error)
        console.error('Error details:', {
          message: error.message,
          stack: error.stack,
          blobSize: blob.size,
          blobType: blob.type
        })
        reject(new Error(`Failed to convert blob to base64: ${error.message || 'Unknown error'}`))
      }
    }
    reader.onerror = (error) => {
      console.error('FileReader error:', error)
      console.error('Error details:', {
        blobSize: blob.size,
        blobType: blob.type,
        error: error
      })
      reject(new Error(`Failed to read video blob: ${error.message || 'Unknown error'}`))
    }
    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = (event.loaded / event.total) * 100
        console.log(`Reading video blob: ${percent.toFixed(1)}% (${event.loaded}/${event.total} bytes)`)
      }
    }
    
    // Read as ArrayBuffer instead of DataURL for more reliable conversion
    reader.readAsArrayBuffer(blob)
  })
}

