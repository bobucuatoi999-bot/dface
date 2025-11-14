/**
 * API service for backend communication
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  login: async (username, password) => {
    // Use URLSearchParams for application/x-www-form-urlencoded format
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    return response.data
  },
  
  getMe: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },
}

// Users API
export const usersAPI = {
  getAll: async () => {
    const response = await api.get('/api/users/')
    return response.data
  },
  
  getById: async (id) => {
    const response = await api.get(`/api/users/${id}`)
    return response.data
  },
  
  create: async (userData) => {
    const response = await api.post('/api/users/', userData)
    return response.data
  },
  
  register: async (name, email, imageData) => {
    const response = await api.post('/api/users/register', {
      name,
      email,
      image_data: imageData
    })
    return response.data
  },
  
  registerWithVideo: async (name, email, employeeId, videoData, minFrames = 5, minQuality = 0.5) => {
    const response = await api.post('/api/users/register/video', {
      name,
      email,
      employee_id: employeeId,
      video_data: videoData,
      min_frames_with_face: minFrames,
      min_quality_score: minQuality
    })
    return response.data
  },
  
  registerMultiAngle: async (name, email, images) => {
    const response = await api.post('/api/users/register/multi-angle', {
      name,
      email,
      images
    })
    return response.data
  },
  
  update: async (id, userData) => {
    const response = await api.put(`/api/users/${id}`, userData)
    return response.data
  },
  
  delete: async (id) => {
    await api.delete(`/api/users/${id}`)
  },
  
  getFaces: async (userId) => {
    const response = await api.get(`/api/users/${userId}/faces`)
    return response.data
  },
  
  addFace: async (userId, imageData, angle = 'frontal') => {
    const response = await api.post(`/api/users/${userId}/faces`, {
      image_data: imageData,
      capture_angle: angle
    })
    return response.data
  },
}

// Logs API
export const logsAPI = {
  getAll: async (filters = {}) => {
    const response = await api.get('/api/logs/', { params: filters })
    return response.data
  },
  
  getStats: async () => {
    const response = await api.get('/api/logs/stats')
    return response.data
  },
  
  getSessions: async (limit = 50) => {
    const response = await api.get('/api/logs/sessions', { params: { limit } })
    return response.data
  },
}

// Search API
export const searchAPI = {
  findSimilar: async (imageData, threshold = 0.6, limit = 10) => {
    const response = await api.get('/api/search/similar', {
      params: { image_data: imageData, threshold, limit }
    })
    return response.data
  },
  
  compareFaces: async (image1Data, image2Data) => {
    const response = await api.post('/api/search/compare', null, {
      params: { image1_data: image1Data, image2_data: image2Data }
    })
    return response.data
  },
}

export default api

