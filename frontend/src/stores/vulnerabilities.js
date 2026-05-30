import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiService from '../services/api'
import { createLogger } from '../utils/logger'

export const useVulnerabilityStore = defineStore('vulnerabilities', () => {
  const logger = createLogger('vulnerabilities')

  const isLoading = ref(false)
  const error = ref(null)

  // Server-side paginated fetch. Wraps the api service so components never call
  // it directly, and returns the raw paginated response ({ data, pagination,
  // headers }) for the usePaginatedData composable.
  const fetchVulnerabilitiesPaginated = async (pagination = {}, filters = {}) => {
    isLoading.value = true
    error.value = null
    try {
      return await apiService.getVulnerabilities(pagination, filters)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load vulnerabilities'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    isLoading,
    error,
    fetchVulnerabilitiesPaginated,
    clearError
  }
})
