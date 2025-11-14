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
      const base64String = reader.result
      // Remove data URL prefix
      const base64 = base64String.includes(',') ? base64String.split(',')[1] : base64String
      resolve(base64)
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

