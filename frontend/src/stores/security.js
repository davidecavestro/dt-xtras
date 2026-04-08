import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSecurityStore = defineStore('security', () => {
  // State
  const securityData = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Computed properties for vulnerability statistics
  const totalVulnerabilities = computed(() => {
    if (!securityData.value || securityData.value.length === 0) return 0
    return securityData.value.reduce((sum, item) => sum + (item.vulnerabilities || 0), 0)
  })

  const criticalVulns = computed(() => {
    if (!securityData.value || securityData.value.length === 0) return 0
    return securityData.value.reduce((sum, item) => sum + (item.critical || 0), 0)
  })

  const highVulns = computed(() => {
    if (!securityData.value || securityData.value.length === 0) return 0
    return securityData.value.reduce((sum, item) => sum + (item.high || 0), 0)
  })

  const mediumVulns = computed(() => {
    if (!securityData.value || securityData.value.length === 0) return 0
    return securityData.value.reduce((sum, item) => sum + (item.medium || 0), 0)
  })

  const lowVulns = computed(() => {
    if (!securityData.value || securityData.value.length === 0) return 0
    return securityData.value.reduce((sum, item) => sum + (item.low || 0), 0)
  })

  const infoVulns = computed(() => {
    return 0 // Info vulnerabilities not currently tracked
  })

  const riskDistribution = computed(() => {
    const critical = criticalVulns.value
    const high = highVulns.value
    const medium = mediumVulns.value
    const low = lowVulns.value
    const info = infoVulns.value

    const riskTotal = critical + high + medium + low

    const distribution = [
      { range: 'Critical', count: critical, percentage: riskTotal > 0 ? Math.round((critical / riskTotal) * 100) : 0 },
      { range: 'High', count: high, percentage: riskTotal > 0 ? Math.round((high / riskTotal) * 100) : 0 },
      { range: 'Medium', count: medium, percentage: riskTotal > 0 ? Math.round((medium / riskTotal) * 100) : 0 },
      { range: 'Low', count: low, percentage: riskTotal > 0 ? Math.round((low / riskTotal) * 100) : 0 }
    ]

    if (info > 0) {
      distribution.push({ range: 'Info', count: info, percentage: 0 })
    }

    return distribution
  })

  // Methods
  const loadSecurityData = async () => {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')

      const response = await axios.get('/api/aggregate')
      securityData.value = response.data

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load security data'
      securityData.value = []
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const refreshSecurityData = async () => {
    await loadSecurityData()
  }

  // Helper function to get security data for specific projects
  const getSecurityDataForProjects = (projects) => {
    if (!projects || projects.length === 0) return []

    return projects
      .filter(project => project.metrics)
      .map(project => ({
        name: project.name,
        type: 'project',
        vulnerabilities: getProjectVulnerabilities(project.metrics),
        critical: project.metrics.critical || 0,
        high: project.metrics.high || 0,
        medium: project.metrics.medium || 0,
        low: project.metrics.low || 0,
        metrics: project.metrics,
        uuid: project.uuid
      }))
  }

  // Helper function to get total vulnerabilities from project metrics
  const getProjectVulnerabilities = (metrics) => {
    if (!metrics) return 0
    return (metrics.critical || 0) + (metrics.high || 0) + (metrics.medium || 0) + (metrics.low || 0)
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  return {
    // State
    securityData,
    isLoading,
    error,
    lastUpdate,

    // Computed
    totalVulnerabilities,
    criticalVulns,
    highVulns,
    mediumVulns,
    lowVulns,
    infoVulns,
    riskDistribution,

    // Methods
    loadSecurityData,
    refreshSecurityData,
    getSecurityDataForProjects,
    getProjectVulnerabilities,
    clearError
  }
})
