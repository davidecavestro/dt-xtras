import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import apiService from '../services/api'
import { createLogger } from '../utils/logger'

export const useProjectStore = defineStore('projects', () => {
  const logger = createLogger('projects')

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
  const projectFilter = ref('')
  const activeOnly = ref(false)
  const selectedTags = ref([])

  // Computed properties
  const filteredProjects = computed(() => {
    let filtered = projects.value

    // Apply project name filter (exact match on name or displayName)
    if (projectFilter.value) {
      const filterName = projectFilter.value.toLowerCase()
      filtered = filtered.filter(project =>
        (project.name && project.name.toLowerCase() === filterName) ||
        (project.displayName && project.displayName.toLowerCase() === filterName)
      )
    }

    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(project =>
        (project.name && project.name.toLowerCase().includes(query)) ||
        (project.displayName && project.displayName.toLowerCase().includes(query)) ||
        (project.version && project.version.toLowerCase().includes(query)) ||
        (project.tags && project.tags.some(tag => tag && tag.name && tag.name.toLowerCase && tag.name.toLowerCase().includes(query)))
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
      // Fetch ALL projects across pages. The list/deck views filter and
      // paginate client-side, so they need the complete portfolio - otherwise
      // the UI only ever shows the backend's default page (50) even when DT has
      // more. The backend honours `limit`/`page` and reports the real total via
      // the X-Total-Count header, which we follow until everything is fetched.
      const FETCH_PAGE_SIZE = 100
      const all = []
      let pageNumber = 1
      let totalCount = null

      while (true) {
        const response = await axios.get('/api/project', {
          params: { page: pageNumber, limit: FETCH_PAGE_SIZE }
        })
        const batch = response.data?.data || response.data || []
        all.push(...batch)

        const header = response.headers?.['x-total-count']
        if (header != null) totalCount = parseInt(header, 10)

        const reachedTotal = totalCount != null && all.length >= totalCount
        if (batch.length === 0 || batch.length < FETCH_PAGE_SIZE || reachedTotal) break
        pageNumber += 1
      }

      logger.debug(`Loaded ${all.length} projects (total reported: ${totalCount})`)
      projects.value = all

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return all
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

  // Server-side paginated fetch used by the projects list view. Wraps the api
  // service so components never call it directly, and returns the raw paginated
  // response ({ data, pagination, headers }) for the usePaginatedData composable.
  const fetchProjectsPaginated = async (pagination = {}, filters = {}) => {
    try {
      return await apiService.getProjects(pagination, filters)
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load projects'
      throw err
    }
  }

  // True server-side page fetch for the Project Center browser. Returns only the
  // requested page plus DT's real total (from the X-Total-Count header), so the
  // view never has to load the whole portfolio. Filtering (name search, active,
  // single tag) is delegated to DT. A `tag` filter routes through DT's per-tag
  // endpoint, which has no name search - so `tag` takes precedence over `search`.
  // This does NOT mutate the shared `projects` state (the bulk-action views rely
  // on that holding the full portfolio); the caller owns the returned rows.
  const fetchProjectsPage = async ({
    page = 1,
    pageSize = 20,
    search = '',
    excludeInactive = true,
    tag = '',
    sortName = '',
    sortOrder = ''
  } = {}) => {
    const params = { page, limit: pageSize, excludeInactive: String(excludeInactive) }
    if (tag) {
      params.tag = tag
    } else if (search) {
      params.search = search
    }
    // Server-side sort (ignored by the search path, which is relevance-ordered).
    if (sortName) {
      params.sortName = sortName
      params.sortOrder = sortOrder === 'desc' ? 'desc' : 'asc'
    }

    try {
      const response = await axios.get('/api/project', { params })
      const rows = response.data?.data || response.data || []
      const header = response.headers?.['x-total-count']
      const total = header != null ? parseInt(header, 10) : rows.length
      return { rows, total }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load projects'
      throw err
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
    return projects.value.filter(project => {
      if (!project.tags || project.tags.length === 0) return false

      // Handle both tag names and tag IDs
      return tags.some(tag => {
        // Check if tag is an object (with id property) or string
        const tagId = typeof tag === 'object' ? tag.id || tag.name : tag
        const tagName = typeof tag === 'object' ? tag.name : tag

        // Check if project has this tag (by ID or name)
        return project.tags.some(projectTag => {
          const projectTagId = typeof projectTag === 'object' ? projectTag.id || projectTag.name : projectTag
          const projectTagName = typeof projectTag === 'object' ? projectTag.name : projectTag

          return projectTagId === tagId || projectTagName === tagName
        })
      })
    })
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

  const bulkActivateProjects = async (projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      await axios.patch('/api/project/batch/activate', {
        projectUuids
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to activate projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const bulkDeactivateProjects = async (projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      await axios.patch('/api/project/batch/deactivate', {
        projectUuids
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to deactivate projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const bulkDeleteProjects = async (projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.delete('/api/project/batch', {
        data: { projectUuids }
      })

      const results = response.data.results
      const successUuids = results.success || []
      const failedUuids = results.failed || []

      // Only remove successfully deleted projects from local state
      successUuids.forEach(uuid => {
        const index = projects.value.findIndex(project => project.uuid === uuid)
        if (index > -1) {
          projects.value.splice(index, 1)
        }
      })

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      // If there were any failures, set error message but don't throw
      if (failedUuids.length > 0) {
        const failureDetails = failedUuids.map(f => f.error || 'Unknown error').join('; ')
        error.value = `Deleted ${successUuids.length} of ${projectUuids.length} projects. Failures: ${failureDetails}`
        // Return partial success info instead of throwing
        return { success: successUuids.length, failed: failedUuids.length, results }
      }

      return { success: successUuids.length, failed: 0, results }
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteProject = async (projectUuid) => {
    isLoading.value = true
    error.value = null

    try {
      // Use the backend batch endpoint (handles deactivate-then-delete) rather than
      // the raw DT proxy, which cannot delete an active project.
      const response = await axios.delete('/api/project/batch', {
        data: { projectUuids: [projectUuid] }
      })

      const results = response.data.results || {}
      const failed = results.failed || []
      if (failed.length > 0) {
        const detail = failed.map(f => f.error || 'Unknown error').join('; ')
        error.value = `Failed to delete project: ${detail}`
        throw new Error(error.value)
      }

      // Remove project from local state
      const index = projects.value.findIndex(project => project.uuid === projectUuid)
      if (index > -1) {
        projects.value.splice(index, 1)
      }

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete project'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const refreshProject = async (projectUuid) => {
    isLoading.value = true
    error.value = null

    try {
      // There is no single-project refresh route; reuse the batch endpoint with
      // a one-element list (it triggers DT's /analysis per project).
      await axios.put('/api/project/batch/refresh', {
        projectUuids: [projectUuid]
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to refresh project'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const bulkRefreshProjects = async (projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      await axios.put('/api/project/batch/refresh', {
        projectUuids
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to refresh projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const bulkRenameProjects = async (projectUuids, newName) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await axios.patch('/api/project/bulk-rename', {
        projectUuids,
        newName
      })

      // Update local project names
      projectUuids.forEach(uuid => {
        const project = projects.value.find(p => p.uuid === uuid)
        if (project) {
          project.name = newName
        }
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to rename projects'
      throw err
    } finally {
      isLoading.value = false
    }
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

  const setProjectFilter = (projectName) => {
    projectFilter.value = projectName
    currentPage.value = 1 // Reset to first page when filtering
    updatePaginationInfo()
  }

  const clearFilters = () => {
    searchQuery.value = ''
    projectFilter.value = ''
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

  // Update page size
  const setPageSize = (newSize) => {
    pageSize.value = newSize
    currentPage.value = 1 // Reset to first page when changing page size
    updatePaginationInfo()
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
    projectFilter,
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
    fetchProjectsPaginated,
    fetchProjectsPage,
    getProjectById,
    getProjectByName,
    getProjectsByTags,
    getActiveProjects,
    getInactiveProjects,
    getProjectCount,
    getActiveProjectCount,
    getInactiveProjectCount,
    bulkActivateProjects,
    bulkDeactivateProjects,
    bulkDeleteProjects,
    deleteProject,
    refreshProject,
    bulkRefreshProjects,
    bulkRenameProjects,
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
    setProjectFilter,
    setActiveFilter,
    setSelectedTags,
    addTagFilter,
    removeTagFilter,
    clearFilters,

    // Utility methods
    refreshProjects,
    clearError,
    resetPagination,
    updatePaginationInfo,
    setPageSize
  }
})
