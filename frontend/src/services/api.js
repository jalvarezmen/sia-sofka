import axios from 'axios'
import { API_BASE_URL } from '../config/constants'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 segundos de timeout
})

// Interceptor para agregar el token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Manejo de errores de autenticación
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // Solo redirigir si no estamos ya en la página de login
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }

    // Manejo de errores de red
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error') {
      console.error('Error de conexión: No se pudo conectar con el servidor')
      return Promise.reject({
        message: 'Error de conexión. Por favor, verifica tu conexión a .',
        isNetworkError: true,
      })
    }

    // Manejo de errores del servidor
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response
      
      // Errores 4xx (cliente)
      if (status >= 400 && status < 500) {
        console.error(`Error del cliente (${status}):`, data)
      }
      
      // Errores 5xx (servidor)
      if (status >= 500) {
        console.error(`Error del servidor (${status}):`, data)
        return Promise.reject({
          message: 'Error del servidor. Por favor, intenta más tarde.',
          status,
          data,
        })
      }

      // Retornar el error con el mensaje del servidor
      return Promise.reject({
        message: data?.detail || data?.message || 'Ha ocurrido un error',
        status,
        data,
      })
    }

    // Error sin respuesta del servidor
    return Promise.reject({
      message: 'Error desconocido. Por favor, intenta nuevamente.',
      originalError: error,
    })
  }
)

export default api
