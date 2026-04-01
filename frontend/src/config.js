// Configuration constants for deployment - use global config from script tag
let config = window.APP_CONFIG || {
  BACKEND_API_URL: 'http://localhost:8000',
  DT_API_URL: 'http://dtrack-apiserver:8080',
  DT_FRONTEND_URL: 'http://dtrack-frontend:8080'
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
