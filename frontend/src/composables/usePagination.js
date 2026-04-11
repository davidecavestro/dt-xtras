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
    logger.info('updatePaginationMetadata - received metadata:', metadata)

    if (metadata.currentPage !== undefined) {
      const currentPageValue = typeof metadata.currentPage === 'object' ? metadata.currentPage.page : metadata.currentPage
      logger.info('updatePaginationMetadata - setting currentPage to:', currentPageValue)
      currentPage.value = currentPageValue
    }
    if (metadata.pageSize !== undefined) {
      const pageSizeValue = typeof metadata.pageSize === 'object' ? metadata.pageSize.pageSize : metadata.pageSize
      logger.info('updatePaginationMetadata - setting pageSize to:', pageSizeValue)
      pageSize.value = pageSizeValue
    }
    if (metadata.totalItems !== undefined) {
      logger.info('updatePaginationMetadata - setting totalItems to:', metadata.totalItems)
      totalItems.value = metadata.totalItems
    }
    if (metadata.totalPages !== undefined) {
      logger.info('updatePaginationMetadata - setting totalPages to:', metadata.totalPages)
      totalPages.value = metadata.totalPages
    } else if (metadata.totalItems !== undefined && metadata.pageSize !== undefined) {
      const pageSizeValue = typeof metadata.pageSize === 'object' ? metadata.pageSize.pageSize : metadata.pageSize
      totalPages.value = Math.ceil(metadata.totalItems / pageSizeValue)
      logger.info('updatePaginationMetadata - calculated totalPages:', totalPages.value)
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
  const {
    initialPage = 1,
    initialPageSize = 20,
    pageSizeOptions = [10, 20, 50, 100]
  } = paginationOptions

  // State
  const currentPage = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const totalItems = ref(0)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref(null)
  const data = ref([])

  const fetchData = async (additionalParams = {}) => {
    loading.value = true
    error.value = null

    try {
      const params = {
        page: currentPage.value,
        pageSize: pageSize.value,
        ...additionalParams
      }

      const response = await fetchFunction(params.page, params.pageSize)

      // Handle DT API response: data array + X-Total-Count header
      if (response.data && Array.isArray(response.data)) {
        data.value = response.data

        // Extract total from X-Total-Count header
        if (response.headers && response.headers['x-total-count']) {
          totalItems.value = parseInt(response.headers['x-total-count'])
          totalPages.value = Math.ceil(totalItems.value / pageSize.value)
        }
      }

      return response
    } catch (err) {
      error.value = err.message || 'Failed to fetch data'
      throw err
    } finally {
      loading.value = false
    }
  }

  const setPage = (page) => {
    currentPage.value = page
  }

  const setPageSize = (newPageSize) => {
    pageSize.value = newPageSize
    currentPage.value = 1
  }

  return {
    data,
    pagination: {
      currentPage,
      pageSize,
      totalItems,
      totalPages,
      loading,
      error,
      setPage,
      setPageSize
    },
    fetchData
  }
}
