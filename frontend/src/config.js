// Configuration constants for deployment
let config = {
  // Load from runtime config file first
  BACKEND_API_URL: 'http://localhost:8000',
  DT_API_URL: 'http://dtrack-apiserver:8080',
  DT_FRONTEND_URL: 'http://dtrack-frontend:8080'
}

// Load runtime configuration from config.json
export const loadConfig = async () => {
  try {
    // Try to load runtime config first
    const response = await fetch('/config.json')
    if (response.ok) {
      const runtimeConfig = await response.json()
      config = {
        BACKEND_API_URL: runtimeConfig.BACKEND_API_URL || config.BACKEND_API_URL,
        DT_API_URL: runtimeConfig.DT_API_URL || config.DT_API_URL,
        DT_FRONTEND_URL: runtimeConfig.DT_FRONTEND_URL || config.DT_FRONTEND_URL
      }
    }
  } catch (error) {
    console.warn('Failed to load runtime config, using defaults:', error)
  }

  // Still try backend API config as fallback
  try {
    const response = await fetch(`${config.BACKEND_API_URL}/api/config`)
    if (response.ok) {
      const backendConfig = await response.json()
      config = {
        BACKEND_API_URL: backendConfig.BACKEND_API_URL || config.BACKEND_API_URL,
        DT_API_URL: backendConfig.DT_API_URL || config.DT_API_URL,
        DT_FRONTEND_URL: backendConfig.DT_FRONTEND_URL || config.DT_FRONTEND_URL
      }
    }
  } catch (error) {
    console.warn('Failed to load config from backend, using defaults:', error)
  }

  return config
}

// Export config getter
export const getConfig = () => config

// Helper functions for building URLs
export const buildDTProjectUrl = (projectUuid) => {
  return `${config.DT_FRONTEND_URL}/projects/${projectUuid}`
}

export const buildDTApiUrl = (endpoint) => {
  return `${config.DT_API_URL}${endpoint}`
}

export const buildBackendApiUrl = (endpoint) => {
  return `${config.BACKEND_API_URL}${endpoint}`
}
