import { describe, it, expect, vi, beforeAll, beforeEach } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => ({
  default: {
    defaults: {},
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

vi.mock('../../config.js', () => ({
  getConfig: () => ({ BACKEND_API_URL: 'http://localhost:8000' })
}))

beforeAll(() => {
  globalThis.logger = { error: vi.fn(), info: vi.fn(), debug: vi.fn(), warn: vi.fn() }
})

describe('ApiService', () => {
  let apiService

  beforeEach(async () => {
    vi.clearAllMocks()
    const mod = await import('../api.js')
    apiService = mod.default
  })

  describe('buildPaginationParams', () => {
    it('returns page-based params by default', () => {
      const params = apiService.buildPaginationParams({ page: 2, pageSize: 50 })
      expect(params).toEqual({ pageNumber: '2', pageSize: '50' })
    })

    it('returns offset-based params when type is offset', () => {
      const params = apiService.buildPaginationParams({ page: 3, pageSize: 20, type: 'offset' })
      expect(params).toEqual({ offset: '40', limit: '20' })
    })

    it('uses defaults when called with empty options', () => {
      const params = apiService.buildPaginationParams()
      expect(params.pageNumber).toBe('1')
      expect(params.pageSize).toBe('100')
    })

    it('calculates offset correctly for page 1', () => {
      const params = apiService.buildPaginationParams({ page: 1, pageSize: 25, type: 'offset' })
      expect(params.offset).toBe('0')
      expect(params.limit).toBe('25')
    })

    it('includes sort params when sortName is provided', () => {
      const params = apiService.buildPaginationParams({ sortName: 'name', sortOrder: 'desc' })
      expect(params.sortName).toBe('name')
      expect(params.sortOrder).toBe('desc')
    })

    it('does not include sort params when sortName is absent', () => {
      const params = apiService.buildPaginationParams({ page: 1 })
      expect(params.sortName).toBeUndefined()
      expect(params.sortOrder).toBeUndefined()
    })
  })

  describe('extractPaginationMetadata', () => {
    it('reads total from x-total-count header', () => {
      const response = { data: [1, 2, 3], headers: { 'x-total-count': '100' } }
      const meta = apiService.extractPaginationMetadata(response, { page: 1, pageSize: 20 })
      expect(meta.totalItems).toBe(100)
      expect(meta.totalPages).toBe(5)
      expect(meta.hasNextPage).toBe(true)
      expect(meta.hasPreviousPage).toBe(false)
    })

    it('falls back to total-count header', () => {
      const response = { data: [1, 2], headers: { 'total-count': '2' } }
      const meta = apiService.extractPaginationMetadata(response, { page: 1, pageSize: 20 })
      expect(meta.totalItems).toBe(2)
    })

    it('infers last page from partial data array', () => {
      const data = [1, 2, 3]
      const response = { data, headers: {} }
      const meta = apiService.extractPaginationMetadata(response, { page: 2, pageSize: 20 })
      expect(meta.totalItems).toBe(23)
      expect(meta.hasNextPage).toBe(false)
    })

    it('marks hasNextPage true when full page returned and no total', () => {
      const data = Array(20).fill(null)
      const response = { data, headers: {} }
      const meta = apiService.extractPaginationMetadata(response, { page: 1, pageSize: 20 })
      expect(meta.hasNextPage).toBe(true)
      expect(meta.totalItems).toBe(-1)
    })

    it('marks hasPreviousPage true on pages after first', () => {
      const response = { data: [], headers: { 'x-total-count': '50' } }
      const meta = apiService.extractPaginationMetadata(response, { page: 3, pageSize: 10 })
      expect(meta.hasPreviousPage).toBe(true)
    })
  })

  describe('getPaginated', () => {
    it('returns structured response when backend returns {data, pagination}', async () => {
      const payload = { data: [{ id: 1 }], pagination: { currentPage: 1, totalPages: 1 } }
      axios.get.mockResolvedValue({ data: payload, headers: {} })

      const result = await apiService.getPaginated('projects', { page: 1 })
      expect(result.data).toEqual(payload.data)
      expect(result.pagination).toEqual(payload.pagination)
    })

    it('extracts pagination from headers when backend returns a plain array', async () => {
      const items = [{ id: 1 }, { id: 2 }]
      axios.get.mockResolvedValue({ data: items, headers: { 'x-total-count': '2' } })

      const result = await apiService.getPaginated('projects', { page: 1, pageSize: 20 })
      expect(result.data).toEqual(items)
      expect(result.pagination.totalItems).toBe(2)
    })

    it('propagates axios errors', async () => {
      axios.get.mockRejectedValue(new Error('Network error'))
      await expect(apiService.getPaginated('projects')).rejects.toThrow('Network error')
    })
  })

  describe('get', () => {
    it('calls axios.get with the correct path and params', async () => {
      axios.get.mockResolvedValue({ data: { result: 'ok' } })
      const result = await apiService.get('/taxonomies', { active: true })
      expect(axios.get).toHaveBeenCalledWith('/api/v1/taxonomies', { params: { active: true } })
      expect(result).toEqual({ result: 'ok' })
    })

    it('merges pagination params when pagination is supplied', async () => {
      axios.get.mockResolvedValue({ data: [] })
      await apiService.get('/tags', {}, { page: 2, pageSize: 10 })
      const call = axios.get.mock.calls[0]
      expect(call[1].params.pageNumber).toBe('2')
      expect(call[1].params.pageSize).toBe('10')
    })

    it('propagates errors', async () => {
      axios.get.mockRejectedValue(new Error('500'))
      await expect(apiService.get('/fail')).rejects.toThrow('500')
    })
  })

  describe('post', () => {
    it('posts data and returns the response body', async () => {
      axios.post.mockResolvedValue({ data: { id: 42 } })
      const result = await apiService.post('/taxonomies', { name: 'sec' })
      expect(axios.post).toHaveBeenCalledWith('/api/v1/taxonomies', { name: 'sec' })
      expect(result).toEqual({ id: 42 })
    })
  })

  describe('put', () => {
    it('puts data and returns the response body', async () => {
      axios.put.mockResolvedValue({ data: { updated: true } })
      const result = await apiService.put('/taxonomies/1', { name: 'updated' })
      expect(axios.put).toHaveBeenCalledWith('/api/v1/taxonomies/1', { name: 'updated' })
      expect(result).toEqual({ updated: true })
    })
  })

  describe('delete', () => {
    it('sends DELETE and returns the response body', async () => {
      axios.delete.mockResolvedValue({ data: null })
      const result = await apiService.delete('/taxonomies/1')
      expect(axios.delete).toHaveBeenCalledWith('/api/v1/taxonomies/1')
      expect(result).toBeNull()
    })
  })
})
