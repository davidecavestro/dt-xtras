import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { createLogger } from '../utils/logger'

export const useTagStore = defineStore('tags', () => {
  const logger = createLogger('tags-store')

  // State
  const tags = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)

  // Pagination state
  const currentPage = ref(1)
  const pageSize = ref(20)
  const totalTags = ref(0)
  const totalPages = ref(1)

  // Search and filter state
  const searchQuery = ref('')
  const selectedTaxonomy = ref('')
  const showCustomOnly = ref(false)

  // Computed properties
  const filteredTags = computed(() => {
    let filtered = tags.value || []

    // Apply search filter
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      filtered = filtered.filter(tag =>
        tag.name.toLowerCase().includes(query)
      )
    }

    // Apply taxonomy filter
    if (selectedTaxonomy.value) {
      filtered = filtered.filter(tag => tag.taxonomy === selectedTaxonomy.value)
    }

    // Apply custom filter
    if (showCustomOnly.value) {
      filtered = filtered.filter(tag => tag.custom === true)
    }

    return filtered
  })

  const paginatedTags = computed(() => {
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    return filteredTags.value.slice(startIndex, endIndex)
  })

  const hasPreviousPage = computed(() => currentPage.value > 1)
  const hasNextPage = computed(() => currentPage.value < totalPages.value)

  // Methods
  const loadTags = async () => {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null

    try {
      // Import here to avoid circular dependency
      const { default: axios } = await import('axios')

      // Load all tags (backend doesn't support pagination)
      const response = await axios.get('/api/tag')
      logger.info('Tags API response:', response.data);
      tags.value = response.data || []

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to load tags'
      tags.value = []
      totalTags.value = 0
      totalPages.value = 1
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updatePaginationInfo = () => {
    const filteredCount = filteredTags.value.length
    totalTags.value = filteredCount
    totalPages.value = Math.ceil(filteredCount / pageSize.value)

    // Adjust current page if it's beyond the new total pages
    if (currentPage.value > totalPages.value && totalPages.value > 0) {
      currentPage.value = totalPages.value
    }
  }

  const createTag = async (tagData) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      const response = await axios.post('/api/tag', tagData)

      // Add new tag to local state
      tags.value.push(response.data)

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to create tag'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateTag = async (tagName, tagData) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      const response = await axios.put(`/api/tag/${tagName}`, tagData)

      // Update tag in local state
      const index = tags.value.findIndex(tag => tag.name === tagName)
      if (index > -1) {
        tags.value[index] = response.data
      }

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to update tag'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteTag = async (tagName) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      await axios.delete(`/api/tag/${tagName}`)

      // Remove tag from local state
      const index = tags.value.findIndex(tag => tag.name === tagName)
      if (index > -1) {
        tags.value.splice(index, 1)
      }

      // Update pagination info
      updatePaginationInfo()

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return true
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to delete tag'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const linkTagsToProjects = async (tagName, projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      const response = await axios.post(`/api/v1/tag/${encodeURIComponent(tagName)}/project`, projectUuids)

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to link tags to projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const unlinkTagsFromProjects = async (tagName, projectUuids) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      const response = await axios.delete(`/api/v1/tag/${encodeURIComponent(tagName)}/project`, {
        projects: projectUuids
      })

      // Update timestamp to trigger watchers
      lastUpdate.value = Date.now()

      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to unlink tags from projects'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const getTagByName = (name) => {
    return tags.value.find(tag => tag.name === name)
  }

  const getTagsByTaxonomy = (taxonomyId) => {
    return tags.value.filter(tag => tag.taxonomy === taxonomyId)
  }

  const getCustomTags = () => {
    return tags.value.filter(tag => tag.custom === true)
  }

  const getTagProjects = async (tagName) => {
    isLoading.value = true
    error.value = null

    try {
      const { default: axios } = await import('axios')

      const response = await axios.get(`/api/tag/${encodeURIComponent(tagName)}/project`)

      return response.data || []
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'Failed to get tag projects'
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

  const setTaxonomyFilter = (taxonomyId) => {
    selectedTaxonomy.value = taxonomyId
    currentPage.value = 1 // Reset to first page when filtering
    updatePaginationInfo()
  }

  const setCustomFilter = (showCustom) => {
    showCustomOnly.value = showCustom
    currentPage.value = 1 // Reset to first page when filtering
    updatePaginationInfo()
  }

  const clearFilters = () => {
    searchQuery.value = ''
    selectedTaxonomy.value = ''
    showCustomOnly.value = false
    currentPage.value = 1
    updatePaginationInfo()
  }

  const refreshTags = async () => {
    await loadTags()
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

  return {
    // State
    tags,
    isLoading,
    error,
    lastUpdate,
    currentPage,
    pageSize,
    totalTags,
    totalPages,
    searchQuery,
    selectedTaxonomy,
    showCustomOnly,

    // Computed
    filteredTags,
    paginatedTags,
    hasPreviousPage,
    hasNextPage,

    // Methods
    loadTags,
    createTag,
    updateTag,
    deleteTag,
    linkTagsToProjects,
    unlinkTagsFromProjects,
    getTagProjects,
    getTagByName,
    getTagsByTaxonomy,
    getCustomTags,

    // Pagination methods
    goToPage,
    nextPage,
    previousPage,
    firstPage,
    lastPage,

    // Filter methods
    setSearchQuery,
    setTaxonomyFilter,
    setCustomFilter,
    clearFilters,

    // Utility methods
    refreshTags,
    clearError,
    resetPagination,
    updatePaginationInfo,
    setPageSize
  }
})
