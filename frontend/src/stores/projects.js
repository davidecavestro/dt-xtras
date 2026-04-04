import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('projects', () => {
  // State
  const projects = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  
  // Pagination state
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalProjects = ref(0)
  const totalPages = ref(1)
  
  // Search and filter state
  const searchQuery = ref('')
  const activeOnly = ref(false)
  const selectedTags = ref([])
  
  // Computed properties
  const filteredProjects = computed(() => {
    let filtered = projects.value

    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(project =>
        project.name.toLowerCase().includes(query) ||
        project.displayName.toLowerCase().includes(query) ||
        project.version.toLowerCase().includes(query) ||
        (project.tags && project.tags.some(tag => tag.toLowerCase().includes(query)))
      )
    }

    // Apply active filter
    if (activeOnly.value) {
      filtered = filtered.filter(project => project.active === true)
    }

    // Apply tag filter
    if (selectedTags.value.length > 0) {
      filtered = filtered.filter(project =>
        project.tags && selectedTags.value.some(tag => project.tags.includes(tag))
      )
    }

    return filtered
  })

  const paginatedProjects = computed(() => {
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    return filteredProjects.value.slice(startIndex, endIndex)
  })

  const hasPreviousPage = computed(() => currentPage.value > 1)
  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  // Activity status helpers
  const getActivityStatus = (project) => {
    if (project.active !== undefined) {
      return project.active ? 'Active' : 'Inactive'
    }
    
    // Fallback to time-based status
    const now = new Date()
    const lastSeen = project.lastSeen ? new Date(project.lastSeen) : null
    
    if (!lastSeen) {
      return 'Unknown'
    }
    
    const daysDiff = Math.floor((now - lastSeen) / (1000 * 60 * 60 * 24))
    
    if (daysDiff <= 7) {
      return 'Recently Active'
    } else if (daysDiff <= 30) {
      return 'Stale'
    } else {
      return 'Old'
    }
  }

  const getActivityStatusClass = (project) => {
    const status = getActivityStatus(project)
    
    switch (status) {
      case 'Active':
        return 'text-green-600 dark:text-green-400'
      case 'Inactive':
        return 'text-red-600 dark:text-red-400'
      case 'Recently Active':
        return 'text-blue-600 dark:text-blue-400'
      case 'Stale':
        return 'text-yellow-600 dark:text-yellow-400'
      case 'Old':
        return 'text-gray-600 dark:text-gray-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }

  // Methods
  const loadProjects = async () => {
    if (isLoading.value) return
    
    isLoading.value = true
    error.value = null
    
    try {
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')
      
      const response = await axios.get('/api/projects')
      projects.value = response.data
      
      // Update pagination info
      updatePaginationInfo()
      
      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load projects'
      projects.value = []
      totalProjects.value = 0
      totalPages.value = 1
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updatePaginationInfo = () => {
    const filteredCount = filteredProjects.value.length
    totalProjects.value = filteredCount
    totalPages.value = Math.ceil(filteredCount / pageSize.value)
    
    // Adjust current page if it's beyond the new total pages
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      currentPage.value = totalPages.value
    }
  }

  const getProjectById = (id) => {
    return projects.value.find(project => project.uuid === id || project.id === id)
  }

  const getProjectByName = (name) => {
    return projects.value.find(project => project.name === name)
  }

  const getProjectsByTags = (tags) => {
    if (!tags || tags.length === 0) return []
    return projects.value.filter(project =>
      project.tags && tags.some(tag => project.tags.includes(tag))
    )
  }

  const getActiveProjects = () => {
    return projects.value.filter(project => project.active === true)
  }

  const getInactiveProjects = () => {
    return projects.value.filter(project => project.active === false)
  }

  const getProjectCount = () => {
    return projects.value.length
  }

  const getActiveProjectCount = () => {
    return projects.value.filter(project => project.active === true).length
  }

  const getInactiveProjectCount = () => {
    return projects.value.filter(project => project.active === false).length
  }

  // Pagination methods
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  const nextPage = () => {
    if (hasNextPage.value) {
      currentPage.value++
    }
  }

  const previousPage = () => {
    if (hasPreviousPage.value) {
      currentPage.value--
    }
  }

  const firstPage = () => {
    currentPage.value = 1
  }

  const lastPage = () => {
    currentPage.value = totalPages.value
  }

  // Filter methods
  const setSearchQuery = (query) => {
    searchQuery.value = query
    currentPage.value = 1 // Reset to first page when searching
    updatePaginationInfo()
  }

  const setActiveFilter = (active) => {
    activeOnly.value = active
    currentPage.value = 1 // Reset to first page when filtering
    updatePaginationInfo()
  }

  const setSelectedTags = (tags) => {
    selectedTags.value = tags
    currentPage.value = 1 // Reset to first page when filtering
    updatePaginationInfo()
  }

  const addTagFilter = (tag) => {
    if (!selectedTags.value.includes(tag)) {
      selectedTags.value.push(tag)
      currentPage.value = 1
      updatePaginationInfo()
    }
  }

  const removeTagFilter = (tag) => {
    const index = selectedTags.value.indexOf(tag)
    if (index > -1) {
      selectedTags.value.splice(index, 1)
      currentPage.value = 1
      updatePaginationInfo()
    }
  }

  const clearFilters = () => {
    searchQuery.value = ''
    activeOnly.value = false
    selectedTags.value = []
    currentPage.value = 1
    updatePaginationInfo()
  }

  const refreshProjects = async () => {
    await loadProjects()
  }

  // Clear error
  const clearError = () => {
    error.value = null
  }

  // Reset pagination
  const resetPagination = () => {
    currentPage.value = 1
    pageSize.value = 20
  }

  // Project statistics
  const getProjectStats = computed(() => {
    const total = projects.value.length
    const active = projects.value.filter(p => p.active === true).length
    const inactive = projects.value.filter(p => p.active === false).length
    const withTags = projects.value.filter(p => p.tags && p.tags.length > 0).length
    
    return {
      total,
      active,
      inactive,
      withTags,
      withoutTags: total - withTags,
      activePercentage: total > 0 ? Math.round((active / total) * 100) : 0,
      inactivePercentage: total > 0 ? Math.round((inactive / total) * 100) : 0
    }
  })

  return {
    // State
    projects,
    isLoading,
    error,
    lastUpdate,
    currentPage,
    pageSize,
    totalProjects,
    totalPages,
    searchQuery,
    activeOnly,
    selectedTags,
    
    // Computed
    filteredProjects,
    paginatedProjects,
    hasPreviousPage,
    hasNextPage,
    getProjectStats,
    
    // Methods
    loadProjects,
    getProjectById,
    getProjectByName,
    getProjectsByTags,
    getActiveProjects,
    getInactiveProjects,
    getProjectCount,
    getActiveProjectCount,
    getInactiveProjectCount,
    getActivityStatus,
    getActivityStatusClass,
    
    // Pagination methods
    goToPage,
    nextPage,
    previousPage,
    firstPage,
    lastPage,
    
    // Filter methods
    setSearchQuery,
    setActiveFilter,
    setSelectedTags,
    addTagFilter,
    removeTagFilter,
    clearFilters,
    
    // Utility methods
    refreshProjects,
    clearError,
    resetPagination,
    updatePaginationInfo
  }
})
