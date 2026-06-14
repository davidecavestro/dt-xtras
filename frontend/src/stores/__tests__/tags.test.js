import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTagStore } from '../tags'

vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('../../utils/logger', () => ({
  createLogger: () => ({ info: vi.fn(), debug: vi.fn(), error: vi.fn(), warn: vi.fn() })
}))

beforeAll(() => {
  globalThis.logger = { error: vi.fn(), info: vi.fn(), debug: vi.fn(), warn: vi.fn() }
})

const makeTag = (overrides = {}) => ({
  name: `tag-${Math.random().toString(36).slice(2)}`,
  taxonomy: 'brand',
  custom: false,
  ...overrides
})

describe('useTagStore', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTagStore()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('starts empty and not loading', () => {
      expect(store.tags).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('defaults to page 1 with pageSize 20', () => {
      expect(store.currentPage).toBe(1)
      expect(store.pageSize).toBe(20)
    })
  })

  describe('filteredTags', () => {
    beforeEach(() => {
      store.tags = [
        makeTag({ name: 'brand:acme', taxonomy: 'brand', custom: false }),
        makeTag({ name: 'region:eu', taxonomy: 'region', custom: false }),
        makeTag({ name: 'custom-tag', taxonomy: 'brand', custom: true })
      ]
    })

    it('returns all tags when no filters are active', () => {
      expect(store.filteredTags).toHaveLength(3)
    })

    it('filters by search query', () => {
      store.searchQuery = 'region'
      expect(store.filteredTags).toHaveLength(1)
      expect(store.filteredTags[0].name).toBe('region:eu')
    })

    it('filters by taxonomy', () => {
      store.selectedTaxonomy = 'brand'
      expect(store.filteredTags).toHaveLength(2)
      expect(store.filteredTags.every(t => t.taxonomy === 'brand')).toBe(true)
    })

    it('filters to custom tags only', () => {
      store.showCustomOnly = true
      expect(store.filteredTags).toHaveLength(1)
      expect(store.filteredTags[0].name).toBe('custom-tag')
    })

    it('stacks multiple filters', () => {
      store.selectedTaxonomy = 'brand'
      store.showCustomOnly = true
      expect(store.filteredTags).toHaveLength(1)
      expect(store.filteredTags[0].custom).toBe(true)
    })
  })

  describe('paginatedTags', () => {
    it('returns page slice when there are more items than pageSize', () => {
      store.tags = Array.from({ length: 30 }, (_, i) => makeTag({ name: `t-${i}` }))
      store.pageSize = 20
      store.currentPage = 1
      expect(store.paginatedTags).toHaveLength(20)
    })

    it('returns remainder on last page', () => {
      store.tags = Array.from({ length: 30 }, (_, i) => makeTag({ name: `t-${i}` }))
      store.pageSize = 20
      store.currentPage = 2
      expect(store.paginatedTags).toHaveLength(10)
    })
  })

  describe('filter methods', () => {
    it('setSearchQuery updates query and resets to page 1', () => {
      store.currentPage = 3
      store.setSearchQuery('brand')
      expect(store.searchQuery).toBe('brand')
      expect(store.currentPage).toBe(1)
    })

    it('setTaxonomyFilter updates taxonomy and resets to page 1', () => {
      store.currentPage = 2
      store.setTaxonomyFilter('region')
      expect(store.selectedTaxonomy).toBe('region')
      expect(store.currentPage).toBe(1)
    })

    it('setCustomFilter updates flag and resets to page 1', () => {
      store.currentPage = 2
      store.setCustomFilter(true)
      expect(store.showCustomOnly).toBe(true)
      expect(store.currentPage).toBe(1)
    })

    it('clearFilters resets all filter state', () => {
      store.searchQuery = 'x'
      store.selectedTaxonomy = 'brand'
      store.showCustomOnly = true
      store.currentPage = 3
      store.clearFilters()
      expect(store.searchQuery).toBe('')
      expect(store.selectedTaxonomy).toBe('')
      expect(store.showCustomOnly).toBe(false)
      expect(store.currentPage).toBe(1)
    })
  })

  describe('pagination methods', () => {
    beforeEach(() => {
      store.tags = Array.from({ length: 50 }, (_, i) => makeTag({ name: `t-${i}` }))
      store.updatePaginationInfo()
    })

    it('nextPage advances when not on last page', () => {
      store.currentPage = 1
      store.nextPage()
      expect(store.currentPage).toBe(2)
    })

    it('previousPage moves back when not on first page', () => {
      store.currentPage = 2
      store.previousPage()
      expect(store.currentPage).toBe(1)
    })

    it('previousPage does not go below 1', () => {
      store.currentPage = 1
      store.previousPage()
      expect(store.currentPage).toBe(1)
    })

    it('firstPage resets to page 1', () => {
      store.currentPage = 3
      store.firstPage()
      expect(store.currentPage).toBe(1)
    })

    it('lastPage jumps to last page', () => {
      store.lastPage()
      expect(store.currentPage).toBe(store.totalPages)
    })

    it('goToPage respects valid bounds', () => {
      store.goToPage(2)
      expect(store.currentPage).toBe(2)
    })

    it('goToPage ignores out-of-bounds values', () => {
      store.goToPage(100)
      expect(store.currentPage).toBe(1)
    })
  })

  describe('loadTags', () => {
    it('populates tags from the API response', async () => {
      const { default: axios } = await import('axios')
      const mockTags = [makeTag({ name: 'brand:x' })]
      axios.get.mockResolvedValue({ data: mockTags })

      await store.loadTags()

      expect(store.tags).toEqual(mockTags)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('sets error and empties tags on failure', async () => {
      const { default: axios } = await import('axios')
      axios.get.mockRejectedValue({ message: 'Network error' })

      await expect(store.loadTags()).rejects.toBeTruthy()
      expect(store.tags).toEqual([])
      expect(store.error).toBeTruthy()
    })

    it('is a no-op while already loading', async () => {
      const { default: axios } = await import('axios')
      store.isLoading = true
      await store.loadTags()
      expect(axios.get).not.toHaveBeenCalled()
    })

    it('reuses fresh data within maxAgeMs instead of refetching', async () => {
      const { default: axios } = await import('axios')
      axios.get.mockResolvedValue({ data: [makeTag({ name: 'brand:x' })] })

      await store.loadTags()
      expect(axios.get).toHaveBeenCalledTimes(1)

      // Within the staleness window: served from memory, no second request.
      await store.loadTags({ maxAgeMs: 60000 })
      expect(axios.get).toHaveBeenCalledTimes(1)
    })

    it('always refetches when maxAgeMs is omitted (default force)', async () => {
      const { default: axios } = await import('axios')
      axios.get.mockResolvedValue({ data: [makeTag({ name: 'brand:x' })] })

      await store.loadTags()
      await store.loadTags()
      expect(axios.get).toHaveBeenCalledTimes(2)
    })
  })

  describe('createTag', () => {
    it('adds the new tag to local state', async () => {
      const { default: axios } = await import('axios')
      const newTag = makeTag({ name: 'brand:new' })
      axios.post.mockResolvedValue({ data: newTag })

      await store.createTag({ name: 'brand:new' })

      expect(store.tags).toContainEqual(newTag)
    })

    it('sets error on failure', async () => {
      const { default: axios } = await import('axios')
      axios.post.mockRejectedValue({ message: 'Conflict' })

      await expect(store.createTag({})).rejects.toBeTruthy()
      expect(store.error).toBeTruthy()
    })
  })

  describe('updateTag', () => {
    it('replaces the tag in local state', async () => {
      const { default: axios } = await import('axios')
      const original = makeTag({ name: 'brand:old', taxonomy: 'brand' })
      store.tags = [original]
      const updated = { ...original, taxonomy: 'region' }
      axios.put.mockResolvedValue({ data: updated })

      await store.updateTag('brand:old', { taxonomy: 'region' })

      expect(store.tags[0].taxonomy).toBe('region')
    })
  })

  describe('deleteTag', () => {
    it('removes the tag from local state', async () => {
      const { default: axios } = await import('axios')
      const tag = makeTag({ name: 'brand:old' })
      store.tags = [tag]
      axios.delete.mockResolvedValue({})

      await store.deleteTag('brand:old')

      expect(store.tags).toHaveLength(0)
    })

    it('sets error on failure', async () => {
      const { default: axios } = await import('axios')
      axios.delete.mockRejectedValue({ message: 'Not found' })

      await expect(store.deleteTag('nonexistent')).rejects.toBeTruthy()
      expect(store.error).toBeTruthy()
    })
  })

  describe('getTagByName / getTagsByTaxonomy / getCustomTags', () => {
    beforeEach(() => {
      store.tags = [
        makeTag({ name: 'brand:acme', taxonomy: 'brand', custom: false }),
        makeTag({ name: 'region:eu', taxonomy: 'region', custom: false }),
        makeTag({ name: 'my-tag', taxonomy: 'brand', custom: true })
      ]
    })

    it('finds a tag by name', () => {
      expect(store.getTagByName('region:eu')).toBeDefined()
    })

    it('returns undefined for unknown name', () => {
      expect(store.getTagByName('nope')).toBeUndefined()
    })

    it('returns tags belonging to a taxonomy', () => {
      expect(store.getTagsByTaxonomy('brand')).toHaveLength(2)
    })

    it('returns only custom tags', () => {
      const custom = store.getCustomTags()
      expect(custom).toHaveLength(1)
      expect(custom[0].custom).toBe(true)
    })
  })

  describe('clearError / resetPagination / setPageSize', () => {
    it('clearError nullifies error state', () => {
      store.error = 'oops'
      store.clearError()
      expect(store.error).toBeNull()
    })

    it('resetPagination resets to defaults', () => {
      store.currentPage = 5
      store.pageSize = 50
      store.resetPagination()
      expect(store.currentPage).toBe(1)
      expect(store.pageSize).toBe(20)
    })

    it('setPageSize updates size and resets page', () => {
      store.currentPage = 3
      store.setPageSize(50)
      expect(store.pageSize).toBe(50)
      expect(store.currentPage).toBe(1)
    })
  })
})
