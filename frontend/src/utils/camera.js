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

export const captureFrame = (videoElement) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    canvas.width = videoElement.videoWidth
    canvas.height = videoElement.videoHeight
    const ctx = canvas.getContext('2d')
    ctx.drawImage(videoElement, 0, 0)
    const imageData = canvas.toDataURL('image/jpeg', 0.8)
    resolve(imageToBase64(imageData))
  })
}

// Video recording utilities
export const startVideoRecording = (videoElement, options = {}) => {
  const {
    duration = 7000, // 7 seconds default
    mimeType = 'video/webm;codecs=vp8,opus'
  } = options

  try {
    const stream = videoElement.srcObject
    if (!stream) {
      throw new Error('No video stream available')
    }

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
    let stoppedManually = false

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        chunks.push(event.data)
        console.log(`Received chunk: ${event.data.size} bytes (total: ${chunks.length} chunks)`)
      }
    }

    const promise = new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          stoppedManually = true
          mediaRecorder.stop()
        }
      }, duration)

      mediaRecorder.onstop = () => {
        clearTimeout(timeout)
        
        // Validate chunks
        if (chunks.length === 0) {
          reject(new Error('No video data recorded. Please try again.'))
          return
        }

        const totalSize = chunks.reduce((sum, chunk) => sum + chunk.size, 0)
        console.log(`Recording stopped. Total chunks: ${chunks.length}, Total size: ${totalSize} bytes`)
        
        // Validate minimum size (at least 1KB for a valid video)
        if (totalSize < 1024) {
          reject(new Error(`Video file is too small (${totalSize} bytes). Recording may have failed.`))
          return
        }

        const blob = new Blob(chunks, { type: selectedMimeType })
        
        // Additional validation: check blob size matches
        if (blob.size !== totalSize) {
          console.warn(`Blob size mismatch: expected ${totalSize}, got ${blob.size}`)
        }

        // Validate blob is not empty
        if (blob.size === 0) {
          reject(new Error('Video blob is empty. Recording may have failed.'))
          return
        }

        console.log(`✅ Video recorded successfully: ${blob.size} bytes, type: ${selectedMimeType}`)
        resolve(blob)
      }

      mediaRecorder.onerror = (error) => {
        clearTimeout(timeout)
        console.error('MediaRecorder error:', error)
        reject(new Error(`Recording error: ${error.error?.message || 'Unknown error'}`))
      }

      // Start recording with timeslice to ensure data is available
      // Timeslice of 100ms means ondataavailable fires every 100ms
      mediaRecorder.start(100)
      console.log(`Started recording with MIME type: ${selectedMimeType}`)
    })

    return { recorder: mediaRecorder, promise, mimeType: selectedMimeType }
  } catch (error) {
    console.error('Error starting video recording:', error)
    throw error
  }
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

    const reader = new FileReader()
    reader.onloadend = () => {
      try {
        const base64String = reader.result
        
        if (!base64String) {
          reject(new Error('Failed to read video blob'))
          return
        }
        
        // Remove data URL prefix (e.g., "data:video/webm;base64,")
        let base64 = base64String
        if (base64String.includes(',')) {
          base64 = base64String.split(',')[1]
        }
        
        // Clean base64 string: remove whitespace, newlines, and any non-base64 characters
        // Base64 only contains: A-Z, a-z, 0-9, +, /, and = (for padding)
        base64 = base64.replace(/[^A-Za-z0-9+/=]/g, '')
        
        // Ensure it's not empty
        if (!base64 || base64.length === 0) {
          reject(new Error('Empty or invalid base64 string after cleaning'))
          return
        }

        // Validate base64 string length (should be at least 1KB in base64 = ~750 bytes)
        if (base64.length < 1000) {
          reject(new Error(`Base64 string too short (${base64.length} chars). Video may be corrupted.`))
          return
        }

        console.log(`✅ Base64 conversion successful: ${base64.length} characters`)
        resolve(base64)
      } catch (error) {
        console.error('Error processing base64 string:', error)
        reject(error)
      }
    }
    reader.onerror = (error) => {
      console.error('FileReader error:', error)
      reject(new Error(`Failed to read video blob: ${error.message || 'Unknown error'}`))
    }
    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const percent = (event.loaded / event.total) * 100
        console.log(`Reading video blob: ${percent.toFixed(1)}%`)
      }
    }
    reader.readAsDataURL(blob)
  })
}

