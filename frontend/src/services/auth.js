import axios from 'axios'
import { getConfig } from '../config.js'

class AuthService {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    this.username = localStorage.getItem('auth_username')
    this.permissions = JSON.parse(localStorage.getItem('auth_permissions') || '[]')
    this.setupAxiosInterceptors()
  }

  setupAxiosInterceptors() {
    // Add request interceptor to include JWT token in all API calls
    axios.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers['Authorization'] = `Bearer ${this.token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Add response interceptor to handle token expiration
    axios.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          this.logout()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async login(username, password) {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post(`${getConfig().BACKEND_API_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      if (response.data.access_token) {
        this.token = response.data.access_token
        this.username = response.data.username
        this.permissions = response.data.permissions || []

        localStorage.setItem('auth_token', this.token)
        localStorage.setItem('auth_username', this.username)
        localStorage.setItem('auth_permissions', JSON.stringify(this.permissions))

        return { success: true }
      } else {
        return {
          success: false,
          error: response.data?.error || 'Login failed'
        }
      }
    } catch (error) {
      logger.error('Login failed:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  async logout() {
    try {
      // Call logout endpoint for consistency (though JWT is stateless)
      await axios.post(`${getConfig().BACKEND_API_URL}/auth/logout`)
    } catch (error) {
      logger.error('Logout failed:', error)
    } finally {
      this.token = null
      this.username = null
      this.permissions = []
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_username')
      localStorage.removeItem('auth_permissions')
    }
  }

  getUsername() {
    return this.username
  }

  getPermissions() {
    return this.permissions
  }

  hasPermission(permission) {
    return this.permissions.includes(permission)
  }

  hasAnyPermission(permissions) {
    return permissions.some(perm => this.permissions.includes(perm))
  }

  isAuthenticated() {
    return !!this.token
  }
}

export default new AuthService()
