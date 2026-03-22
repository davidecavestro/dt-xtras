import { ref, reactive, computed } from 'vue'

/**
 * Composable for managing pagination state and logic
 * @param {Object} options - Configuration options
 * @param {number} options.initialPage - Initial page number (default: 1)
 * @param {number} options.initialPageSize - Initial page size (default: 20)
 * @param {Array} options.pageSizeOptions - Available page sizes (default: [10, 20, 50, 100])
 * @returns {Object} - Pagination state and methods
 */
export function usePagination(options = {}) {
  const {
    initialPage = 1,
    initialPageSize = 20,
    pageSizeOptions = [10, 20, 50, 100]
  } = options

  // State
  const currentPage = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const totalItems = ref(0)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref(null)

  // Computed properties
  const startItem = computed(() => {
    if (totalItems.value === 0) return 0
    return (currentPage.value - 1) * pageSize.value + 1
  })

  const endItem = computed(() => {
    const end = currentPage.value * pageSize.value
    return Math.min(end, totalItems.value)
  })

  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPreviousPage = computed(() => currentPage.value > 1)

  // Methods
  const setPage = (page) => {
    if (page >= 1 && page <= totalPages.value) {
      currentPage.value = page
    }
  }

  const setPageSize = (newPageSize) => {
    if (pageSizeOptions.includes(newPageSize)) {
      pageSize.value = newPageSize
      currentPage.value = 1 // Reset to first page when changing page size
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

  const reset = () => {
    currentPage.value = initialPage
    pageSize.value = initialPageSize
    totalItems.value = 0
    totalPages.value = 0
    loading.value = false
    error.value = null
  }

  const updatePaginationMetadata = (metadata) => {
    if (metadata.currentPage !== undefined) {
      currentPage.value = metadata.currentPage
    }
    if (metadata.pageSize !== undefined) {
      pageSize.value = metadata.pageSize
    }
    if (metadata.totalItems !== undefined) {
      totalItems.value = metadata.totalItems
    }
    if (metadata.totalPages !== undefined) {
      totalPages.value = metadata.totalPages
    } else if (metadata.totalItems !== undefined && metadata.pageSize !== undefined) {
      totalPages.value = Math.ceil(metadata.totalItems / metadata.pageSize)
    }
  }

  const setLoading = (isLoading) => {
    loading.value = isLoading
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  // Return reactive object for easy consumption
  return reactive({
    // State
    currentPage,
    pageSize,
    totalItems,
    totalPages,
    loading,
    error,

    // Computed
    startItem,
    endItem,
    hasNextPage,
    hasPreviousPage,

    // Methods
    setPage,
    setPageSize,
    nextPage,
    previousPage,
    firstPage,
    lastPage,
    reset,
    updatePaginationMetadata,
    setLoading,
    setError,
    clearError,

    // Options
    pageSizeOptions
  })
}

/**
 * Composable for paginated data fetching
 * @param {Function} fetchFunction - Function that fetches data with pagination
 * @param {Object} paginationOptions - Pagination configuration
 * @returns {Object} - Data, pagination state, and fetch methods
 */
export function usePaginatedData(fetchFunction, paginationOptions = {}) {
  const pagination = usePagination(paginationOptions)
  const data = ref([])
  const lastFetchParams = ref({})

  const fetchData = async (additionalParams = {}) => {
    pagination.setLoading(true)
    pagination.clearError()

    try {
      const params = {
        page: pagination.currentPage,
        pageSize: pagination.pageSize,
        ...additionalParams
      }

      lastFetchParams.value = { ...params }

      const response = await fetchFunction(params)

      // Handle different response formats
      if (response && typeof response === 'object') {
        if (response.data && response.pagination) {
          // Response has data and pagination metadata
          data.value = response.data
          pagination.updatePaginationMetadata(response.pagination)
        } else if (Array.isArray(response)) {
          // Response is just an array, update data
          data.value = response
          // Note: In this case, pagination metadata should be set separately
        } else {
          // Response is a single object
          data.value = [response]
        }
      }

      return response
    } catch (err) {
      pagination.setError(err.message || 'Failed to fetch data')
      throw err
    } finally {
      pagination.setLoading(false)
    }
  }

  const refresh = () => {
    return fetchData(lastFetchParams.value)
  }

  const reset = () => {
    pagination.reset()
    data.value = []
    lastFetchParams.value = {}
  }

  return {
    data,
    pagination,
    fetchData,
    refresh,
    reset
  }
}
