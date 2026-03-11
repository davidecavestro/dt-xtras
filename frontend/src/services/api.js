import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  /**
   * Build pagination parameters for API requests
   * Based on DT OpenAPI spec, supports both pageNumber/pageSize and offset/limit
   * @param {Object} pagination - Pagination configuration
   * @param {number} pagination.page - Current page number (1-based)
   * @param {number} pagination.pageSize - Number of items per page
   * @param {string} pagination.type - Pagination type: 'page' or 'offset'
   * @param {string} pagination.sortName - Field to sort by
   * @param {string} pagination.sortOrder - Sort order: 'asc' or 'desc'
   * @returns {Object} - Query parameters object
   */
  buildPaginationParams(pagination = {}) {
    const {
      page = 1,
      pageSize = 100, // DT default is 100
      type = 'page',
      sortName,
      sortOrder = 'asc'
    } = pagination

    const params = {}

    if (type === 'offset') {
      params.offset = String((page - 1) * pageSize)
      params.limit = String(pageSize)
    } else {
      params.pageNumber = String(page)
      params.pageSize = String(pageSize)
    }

    // Add sorting if specified
    if (sortName) {
      params.sortName = sortName
      params.sortOrder = sortOrder
    }

    return params
  }

  /**
   * Make a paginated API request
   * @param {string} endpoint - API endpoint (relative to /api/v1)
   * @param {Object} pagination - Pagination configuration
   * @param {Object} additionalParams - Additional query parameters
   * @returns {Promise} - API response with pagination metadata
   */
  async getPaginated(endpoint, pagination = {}, additionalParams = {}) {
    const params = {
      ...this.buildPaginationParams(pagination),
      ...additionalParams
    }

    try {
      const response = await axios.get(`${this.baseURL}/api/v1${endpoint}`, { params })

      // Extract pagination metadata from response
      const paginationMetadata = this.extractPaginationMetadata(response, pagination)

      return {
        data: response.data,
        pagination: paginationMetadata,
        headers: response.headers
      }
    } catch (error) {
      console.error(`Error fetching paginated data from ${endpoint}:`, error)
      throw error
    }
  }

  /**
   * Extract pagination metadata from API response
   * DT API typically returns arrays, so we need to calculate pagination ourselves
   * @param {Object} response - Axios response object
   * @param {Object} requestPagination - Request pagination parameters
   * @returns {Object} - Pagination metadata
   */
  extractPaginationMetadata(response, requestPagination = {}) {
    const data = response.data
    const headers = response.headers

    // DT API typically returns arrays directly, so we need to infer pagination
    let metadata = {
      currentPage: requestPagination.page || 1,
      pageSize: requestPagination.pageSize || 100,
      totalItems: 0,
      totalPages: 0,
      hasNextPage: false,
      hasPreviousPage: false
    }

    // Try to get total count from headers first
    if (headers['x-total-count']) {
      metadata.totalItems = parseInt(headers['x-total-count'])
    } else if (headers['total-count']) {
      metadata.totalItems = parseInt(headers['total-count'])
    }

    // If data is an array, we can use its length for current page items
    if (Array.isArray(data)) {
      // If we got fewer items than requested, we're likely on the last page
      if (data.length < metadata.pageSize) {
        metadata.totalItems = (metadata.currentPage - 1) * metadata.pageSize + data.length
      }

      // If we don't have total items but got a full page, we can't determine total
      if (metadata.totalItems === 0 && data.length === metadata.pageSize) {
        // Unknown total - indicate that there might be more pages
        metadata.hasNextPage = true
        metadata.totalItems = -1 // -1 indicates unknown total
      }
    }

    // Calculate derived values
    if (metadata.totalItems > 0) {
      metadata.totalPages = Math.ceil(metadata.totalItems / metadata.pageSize)
      metadata.hasNextPage = metadata.currentPage < metadata.totalPages
      metadata.hasPreviousPage = metadata.currentPage > 1
    } else if (metadata.totalItems === -1) {
      // Unknown total - determine if there might be more pages
      metadata.hasNextPage = Array.isArray(data) && data.length === metadata.pageSize
      metadata.hasPreviousPage = metadata.currentPage > 1
      metadata.totalPages = -1 // Unknown
    }

    return metadata
  }

  /**
   * Generic GET request with optional pagination
   * @param {string} endpoint - API endpoint (relative to /api/v1)
   * @param {Object} params - Query parameters
   * @param {Object} pagination - Pagination configuration
   * @returns {Promise} - API response
   */
  async get(endpoint, params = {}, pagination = null) {
    const queryParams = { ...params }

    if (pagination) {
      Object.assign(queryParams, this.buildPaginationParams(pagination))
    }

    try {
      const response = await axios.get(`${this.baseURL}/api/v1${endpoint}`, {
        params: queryParams
      })
      return response.data
    } catch (error) {
      console.error(`Error fetching data from ${endpoint}:`, error)
      throw error
    }
  }

  /**
   * POST request
   * @param {string} endpoint - API endpoint (relative to /api/v1)
   * @param {Object} data - Request body
   * @returns {Promise} - API response
   */
  async post(endpoint, data = {}) {
    try {
      const response = await axios.post(`${this.baseURL}/api/v1${endpoint}`, data)
      return response.data
    } catch (error) {
      console.error(`Error posting data to ${endpoint}:`, error)
      throw error
    }
  }

  /**
   * PUT request
   * @param {string} endpoint - API endpoint (relative to /api/v1)
   * @param {Object} data - Request body
   * @returns {Promise} - API response
   */
  async put(endpoint, data = {}) {
    try {
      const response = await axios.put(`${this.baseURL}/api/v1${endpoint}`, data)
      return response.data
    } catch (error) {
      console.error(`Error updating data at ${endpoint}:`, error)
      throw error
    }
  }

  /**
   * DELETE request
   * @param {string} endpoint - API endpoint (relative to /api/v1)
   * @returns {Promise} - API response
   */
  async delete(endpoint) {
    try {
      const response = await axios.delete(`${this.baseURL}/api/v1${endpoint}`)
      return response.data
    } catch (error) {
      console.error(`Error deleting data at ${endpoint}:`, error)
      throw error
    }
  }

  // DT API specific endpoints with pagination support
  // All endpoints are now proxied through the backend

  /**
   * Get projects with pagination
   * Endpoint: /project
   * Operation: getProjects
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated projects data
   */
  async getProjects(pagination = {}, filters = {}) {
    return this.getPaginated('/project', pagination, filters)
  }

  /**
   * Get vulnerabilities with pagination
   * Endpoint: /vulnerability
   * Operation: getVulnerabilities
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated vulnerabilities data
   */
  async getVulnerabilities(pagination = {}, filters = {}) {
    return this.getPaginated('/vulnerability', pagination, filters)
  }

  /**
   * Get licenses with pagination
   * Endpoint: /license
   * Operation: getLicenses
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated licenses data
   */
  async getLicenses(pagination = {}, filters = {}) {
    return this.getPaginated('/license', pagination, filters)
  }

  /**
   * Get CWEs with pagination
   * Endpoint: /cwe
   * Operation: getCwes
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated CWEs data
   */
  async getCwes(pagination = {}, filters = {}) {
    return this.getPaginated('/cwe', pagination, filters)
  }

  /**
   * Get license groups with pagination
   * Endpoint: /licenseGroup
   * Operation: getLicenseGroups
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated license groups data
   */
  async getLicenseGroups(pagination = {}, filters = {}) {
    return this.getPaginated('/licenseGroup', pagination, filters)
  }

  /**
   * Get projects for a specific team with pagination
   * Endpoint: /acl/team/{uuid}
   * Operation: retrieveProjects
   * @param {string} teamUuid - Team UUID
   * @param {Object} pagination - Pagination configuration
   * @param {Object} filters - Additional filters
   * @returns {Promise} - Paginated projects data
   */
  async getTeamProjects(teamUuid, pagination = {}, filters = {}) {
    return this.getPaginated(`/acl/team/${teamUuid}`, pagination, filters)
  }
}

export default new ApiService()
