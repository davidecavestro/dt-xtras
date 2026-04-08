import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useProjectStore } from './projects'
import { useTagStore } from './tags'
import { useTaxonomyStore } from './taxonomies'
import { useSecurityStore } from './security'

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const isInitialized = ref(false)
  const isLoading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Store instances
  const projectStore = useProjectStore()
  const tagStore = useTagStore()
  const taxonomyStore = useTaxonomyStore()
  const securityStore = useSecurityStore()

  // Computed properties for coordinated loading state
  const isLoadingAny = computed(() =>
    projectStore.isLoading ||
    tagStore.isLoading ||
    taxonomyStore.loading ||
    securityStore.isLoading
  )

  const hasAnyError = computed(() =>
    projectStore.error ||
    tagStore.error ||
    taxonomyStore.error ||
    securityStore.error
  )

  const isDataReady = computed(() => {
    return (
      projectStore.projects.length > 0 &&
      tagStore.tags.length > 0 &&
      taxonomyStore.taxonomies.length > 0 &&
      securityStore.securityData.length > 0
    )
  })

  // Coordinated loading state - only shows as ready when all data is loaded
  const isFullyLoaded = computed(() => {
    return isInitialized.value && !isLoadingAny.value && isDataReady.value
  })

  // Show loading state until all data is ready
  const shouldShowLoading = computed(() => {
    return !isFullyLoaded.value
  })

  const allErrors = computed(() => {
    const errors = []
    if (projectStore.error) errors.push({ store: 'projects', error: projectStore.error })
    if (tagStore.error) errors.push({ store: 'tags', error: tagStore.error })
    if (taxonomyStore.error) errors.push({ store: 'taxonomies', error: taxonomyStore.error })
    if (securityStore.error) errors.push({ store: 'security', error: securityStore.error })
    return errors
  })

  // Methods
  const loadAllData = async () => {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      // Load all data in parallel for better performance
      await Promise.all([
        projectStore.loadProjects(),
        tagStore.loadTags(),
        taxonomyStore.loadTaxonomies(),
        securityStore.loadSecurityData()
      ])

      isInitialized.value = true
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.message || 'Failed to load dashboard data'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // Method to ensure all data is loaded and ready
  const ensureDataReady = async () => {
    if (!isFullyLoaded.value) {
      await loadAllData()
    }
    return isFullyLoaded.value
  }

  const refreshAllData = async () => {
    // Clear all errors before refreshing
    projectStore.clearError()
    tagStore.clearError()
    taxonomyStore.clearError()
    securityStore.clearError()

    await loadAllData()
  }

  const refreshProjects = async () => {
    try {
      await projectStore.refreshProjects()
      lastUpdate.value = Date.now()
    } catch (err) {
      error.value = `Failed to refresh projects: ${err.message}`
      throw err
    }
  }

  const refreshTags = async () => {
    try {
      await tagStore.refreshTags()
      lastUpdate.value = Date.now()
    } catch (err) {
      error.value = `Failed to refresh tags: ${err.message}`
      throw err
    }
  }

  const refreshTaxonomies = async () => {
    try {
      await taxonomyStore.refreshTaxonomies()
      lastUpdate.value = Date.now()
    } catch (err) {
      error.value = `Failed to refresh taxonomies: ${err.message}`
      throw err
    }
  }

  const refreshSecurity = async () => {
    try {
      await securityStore.refreshSecurityData()
      lastUpdate.value = Date.now()
    } catch (err) {
      error.value = `Failed to refresh security data: ${err.message}`
      throw err
    }
  }

  // Selective refresh methods for when only specific data needs updating
  const loadIfNotReady = async () => {
    if (!isInitialized.value && !isLoading.value) {
      await loadAllData()
    }
  }

  // Clear all errors
  const clearAllErrors = () => {
    projectStore.clearError()
    tagStore.clearError()
    taxonomyStore.clearError()
    securityStore.clearError()
    error.value = null
  }

  // Get dashboard statistics
  const getDashboardStats = computed(() => {
    return {
      projects: projectStore.projects.length,
      tags: tagStore.tags.length,
      taxonomies: taxonomyStore.taxonomies.length,
      vulnerabilities: securityStore.totalVulnerabilities,
      criticalVulns: securityStore.criticalVulns,
      highVulns: securityStore.highVulns,
      mediumVulns: securityStore.mediumVulns,
      lowVulns: securityStore.lowVulns,
      lastUpdate: lastUpdate.value
    }
  })

  // Reset dashboard state
  const reset = () => {
    isInitialized.value = false
    isLoading.value = false
    error.value = null
    lastUpdate.value = null
    clearAllErrors()
  }

  return {
    // State
    isInitialized,
    isLoading,
    error,
    lastUpdate,

    // Computed
    isLoadingAny,
    hasAnyError,
    isDataReady,
    isFullyLoaded,
    shouldShowLoading,
    allErrors,
    getDashboardStats,

    // Methods
    loadAllData,
    ensureDataReady,
    refreshAllData,
    refreshProjects,
    refreshTags,
    refreshTaxonomies,
    refreshSecurity,
    loadIfNotReady,
    clearAllErrors,
    reset,

    // Store access (for direct access if needed)
    projectStore,
    tagStore,
    taxonomyStore,
    securityStore
  }
})
