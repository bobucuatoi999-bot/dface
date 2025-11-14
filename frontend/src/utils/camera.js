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

