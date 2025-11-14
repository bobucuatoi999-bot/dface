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

    const mediaRecorder = new MediaRecorder(stream, { mimeType })
    const chunks = []

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data)
      }
    }

    const promise = new Promise((resolve, reject) => {
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mimeType })
        resolve(blob)
      }

      mediaRecorder.onerror = (error) => {
        reject(error)
      }

      mediaRecorder.start()

      // Auto-stop after duration
      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop()
        }
      }, duration)
    })

    return { recorder: mediaRecorder, promise }
  } catch (error) {
    console.error('Error starting video recording:', error)
    throw error
  }
}

export const videoBlobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
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
          reject(new Error('Empty or invalid base64 string'))
          return
        }
        
        resolve(base64)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = (error) => {
      reject(new Error(`Failed to read video blob: ${error.message || 'Unknown error'}`))
    }
    reader.readAsDataURL(blob)
  })
}

