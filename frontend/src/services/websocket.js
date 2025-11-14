/**
 * WebSocket service for real-time recognition
 */

class RecognitionWebSocket {
  constructor() {
    this.ws = null
    this.sessionId = null
    this.onFrameResult = null
    this.onConnectionChange = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect() {
    return new Promise((resolve, reject) => {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/recognize'
      
      try {
        this.ws = new WebSocket(wsUrl)
        
        this.ws.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          if (this.onConnectionChange) {
            this.onConnectionChange(true)
          }
          resolve()
        }
        
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('Error parsing WebSocket message:', error)
          }
        }
        
        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error)
          if (this.onConnectionChange) {
            this.onConnectionChange(false)
          }
          reject(error)
        }
        
        this.ws.onclose = () => {
          console.log('WebSocket disconnected')
          if (this.onConnectionChange) {
            this.onConnectionChange(false)
          }
          
          // Attempt reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
            setTimeout(() => this.connect(), 3000)
          }
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  handleMessage(data) {
    switch (data.type) {
      case 'connection_established':
        this.sessionId = data.session_id
        console.log('Session ID:', this.sessionId)
        break
        
      case 'recognition_result':
        if (this.onFrameResult) {
          this.onFrameResult(data)
        }
        break
        
      case 'error':
        console.error('WebSocket error:', data.message)
        break
        
      case 'pong':
        // Heartbeat response
        break
        
      default:
        console.log('Unknown message type:', data.type)
    }
  }

  sendFrame(imageData, frameId, timestamp) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'frame',
        data: imageData,
        timestamp: timestamp || Date.now(),
        frame_id: frameId
      }))
    } else {
      console.warn('WebSocket not connected')
    }
  }

  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'ping',
        timestamp: Date.now()
      }))
    }
  }

  reset() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'reset'
      }))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export default new RecognitionWebSocket()

