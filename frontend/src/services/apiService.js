/**
 * Servicio de API con métodos helper para las diferentes entidades
 * Facilita el uso de la API desde los componentes
 */

import api from './api'

// ==================== AUTH ====================
export const authService = {
  login: async (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },
}

// ==================== USERS ====================
export const userService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/users', { params: { skip, limit } })
    return response.data
  },

  getById: async (userId) => {
    const response = await api.get(`/users/${userId}`)
    return response.data
  },

  create: async (userData) => {
    const response = await api.post('/users', userData)
    return response.data
  },

  update: async (userId, userData) => {
    const response = await api.put(`/users/${userId}`, userData)
    return response.data
  },

  delete: async (userId) => {
    await api.delete(`/users/${userId}`)
  },
}

// ==================== SUBJECTS ====================
export const subjectService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/subjects', { params: { skip, limit } })
    return response.data
  },

  getById: async (subjectId) => {
    const response = await api.get(`/subjects/${subjectId}`)
    return response.data
  },

  create: async (subjectData) => {
    const response = await api.post('/subjects', subjectData)
    return response.data
  },

  update: async (subjectId, subjectData) => {
    const response = await api.put(`/subjects/${subjectId}`, subjectData)
    return response.data
  },

  delete: async (subjectId) => {
    await api.delete(`/subjects/${subjectId}`)
  },
}

// ==================== ENROLLMENTS ====================
export const enrollmentService = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await api.get('/enrollments', { params: { skip, limit } })
    return response.data
  },

  getById: async (enrollmentId) => {
    const response = await api.get(`/enrollments/${enrollmentId}`)
    return response.data
  },

  create: async (enrollmentData) => {
    const response = await api.post('/enrollments', enrollmentData)
    return response.data
  },

  delete: async (enrollmentId) => {
    await api.delete(`/enrollments/${enrollmentId}`)
  },
}

// ==================== GRADES ====================
export const gradeService = {
  getAll: async (params = {}) => {
    const response = await api.get('/grades', { params })
    return response.data
  },

  getById: async (gradeId) => {
    const response = await api.get(`/grades/${gradeId}`)
    return response.data
  },

  create: async (gradeData, subjectId) => {
    const response = await api.post('/grades', gradeData, {
      params: { subject_id: subjectId },
    })
    return response.data
  },

  update: async (gradeId, gradeData) => {
    const response = await api.put(`/grades/${gradeId}`, gradeData)
    return response.data
  },

  delete: async (gradeId) => {
    await api.delete(`/grades/${gradeId}`)
  },
}

// ==================== REPORTS ====================
export const reportService = {
  getStudentReport: async (estudianteId, format = 'json') => {
    const response = await api.get(`/reports/student/${estudianteId}`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },

  getSubjectReport: async (subjectId, format = 'pdf') => {
    const response = await api.get(`/reports/subject/${subjectId}`, {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },

  getGeneralReport: async (format = 'pdf') => {
    const response = await api.get('/reports/general', {
      params: { format },
      responseType: format === 'json' ? 'json' : 'blob',
    })
    return response.data
  },
}

// ==================== PROFILE ====================
export const profileService = {
  get: async () => {
    const response = await api.get('/profile')
    return response.data
  },

  update: async (profileData) => {
    const response = await api.put('/profile', profileData)
    return response.data
  },
}

