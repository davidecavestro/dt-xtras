import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class AuthService {
  constructor() {
    this.token = localStorage.getItem('auth_token')
    this.setupAxiosInterceptors()
  }

  setupAxiosInterceptors() {
    // Add request interceptor to include token in all API calls
    axios.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`
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

      const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      this.token = response.data
      this.username = username
      localStorage.setItem('auth_token', this.token)
      localStorage.setItem('auth_username', this.username)

      return { success: true }
    } catch (error) {
      console.error('Login failed:', error)
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed'
      }
    }
  }

  async logout() {
    try {
      if (this.token) {
        // Call backend logout endpoint to invalidate the token
        await axios.post(`${API_BASE_URL}/auth/logout`, {}, {
          headers: {
            'Authorization': `Bearer ${this.token}`
          }
        })
      }
    } catch (error) {
      console.error('Backend logout error:', error)
      // Continue with local logout even if backend call fails
    } finally {
      // Always clear local auth state
      this.token = null
      this.username = ''
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_username')
    }
  }

  getUsername() {
    return this.username
  }

  isAuthenticated() {
    return !!this.token
  }

  getToken() {
    return this.token
  }
}

export default new AuthService()
