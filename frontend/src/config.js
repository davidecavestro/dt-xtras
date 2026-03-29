// Configuration constants for deployment
let config = {
  // Dependency-Track API URL
  DT_API_URL: import.meta.env.VITE_DT_API_URL || __DT_API_URL__ || process.env.DT_API_URL || 'http://dtrack-apiserver:8080',

  // Dependency-Track Frontend URL
  DT_FRONTEND_URL: import.meta.env.VITE_DT_FRONTEND_URL || __DT_FRONTEND_URL__ || process.env.DT_FRONTEND_URL || 'http://dtrack-frontend:8080',

  // Backend API URL
  BACKEND_API_URL: import.meta.env.VITE_BACKEND_API_URL || __BACKEND_API_URL__ || process.env.BACKEND_API_URL || 'http://localhost:8000'
}

// Function to load config from backend API
export const loadConfig = async () => {
  try {
    const response = await fetch(`${config.BACKEND_API_URL}/api/config`)
    if (response.ok) {
      const backendConfig = await response.json()
      config = {
        DT_API_URL: backendConfig.DT_API_URL || config.DT_API_URL,
        DT_FRONTEND_URL: backendConfig.DT_FRONTEND_URL || config.DT_FRONTEND_URL,
        BACKEND_API_URL: backendConfig.BACKEND_API_URL || config.BACKEND_API_URL
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
