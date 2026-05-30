import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '../projects'

vi.mock('axios', () => ({
  default: {
    defaults: {},
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

// The store imports the api service (which constructs ApiService on import);
// mock it so the store is tested in isolation from the real HTTP layer.
vi.mock('../../services/api', () => ({
  default: { getProjects: vi.fn() }
}))

vi.mock('../../utils/logger', () => ({
  createLogger: () => ({ info: vi.fn(), debug: vi.fn(), error: vi.fn(), warn: vi.fn() })
}))

beforeAll(() => {
  globalThis.logger = { error: vi.fn(), info: vi.fn(), debug: vi.fn(), warn: vi.fn() }
})

const makeProject = (overrides = {}) => ({
  uuid: crypto.randomUUID(),
  name: 'project-a',
  version: '1.0',
  active: true,
  tags: [],
  ...overrides
})

describe('useProjectStore', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useProjectStore()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('starts with empty projects and no loading', () => {
      expect(store.projects).toEqual([])
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('starts on page 1 with pageSize 20', () => {
      expect(store.currentPage).toBe(1)
      expect(store.pageSize).toBe(20)
    })
  })

  describe('filteredProjects', () => {
    beforeEach(() => {
      store.projects = [
        makeProject({ uuid: '1', name: 'alpha', active: true, tags: [{ name: 'sec' }] }),
        makeProject({ uuid: '2', name: 'beta', active: false, tags: [] }),
        makeProject({ uuid: '3', name: 'gamma', version: '2.0', active: true, tags: [{ name: 'ops' }] })
      ]
    })

    it('returns all projects when no filters are active', () => {
      expect(store.filteredProjects).toHaveLength(3)
    })

    it('filters by search query on name', () => {
      store.searchQuery = 'alph'
      expect(store.filteredProjects).toHaveLength(1)
      expect(store.filteredProjects[0].name).toBe('alpha')
    })

    it('filters by search query on version', () => {
      store.searchQuery = '2.0'
      expect(store.filteredProjects).toHaveLength(1)
      expect(store.filteredProjects[0].name).toBe('gamma')
    })

    it('filters by search query on tag name', () => {
      store.searchQuery = 'sec'
      expect(store.filteredProjects).toHaveLength(1)
      expect(store.filteredProjects[0].name).toBe('alpha')
    })

    it('filters to active-only when activeOnly is true', () => {
      store.activeOnly = true
      expect(store.filteredProjects).toHaveLength(2)
      expect(store.filteredProjects.every(p => p.active)).toBe(true)
    })

    it('filters by exact project name via projectFilter', () => {
      store.projectFilter = 'beta'
      expect(store.filteredProjects).toHaveLength(1)
      expect(store.filteredProjects[0].name).toBe('beta')
    })

    it('returns empty when projectFilter matches nothing', () => {
      store.projectFilter = 'nonexistent'
      expect(store.filteredProjects).toHaveLength(0)
    })
  })

  describe('paginatedProjects', () => {
    it('returns a slice of filtered projects for the current page', () => {
      store.projects = Array.from({ length: 25 }, (_, i) =>
        makeProject({ uuid: String(i), name: `proj-${i}` })
      )
      store.pageSize = 20
      store.currentPage = 1
      expect(store.paginatedProjects).toHaveLength(20)
    })

    it('returns remaining items on the last page', () => {
      store.projects = Array.from({ length: 25 }, (_, i) =>
        makeProject({ uuid: String(i), name: `proj-${i}` })
      )
      store.pageSize = 20
      store.currentPage = 2
      expect(store.paginatedProjects).toHaveLength(5)
    })
  })

  describe('getProjectStats', () => {
    it('computes correct totals', () => {
      store.projects = [
        makeProject({ active: true, tags: [{ name: 'x' }] }),
        makeProject({ active: false, tags: [] }),
        makeProject({ active: true, tags: [] })
      ]
      const stats = store.getProjectStats
      expect(stats.total).toBe(3)
      expect(stats.active).toBe(2)
      expect(stats.inactive).toBe(1)
      expect(stats.withTags).toBe(1)
      expect(stats.withoutTags).toBe(2)
    })

    it('returns 0 percentages when no projects', () => {
      const stats = store.getProjectStats
      expect(stats.activePercentage).toBe(0)
      expect(stats.inactivePercentage).toBe(0)
    })
  })

  describe('getActivityStatus', () => {
    it('returns Active for projects with active:true', () => {
      expect(store.getActivityStatus({ active: true })).toBe('Active')
    })

    it('returns Inactive for projects with active:false', () => {
      expect(store.getActivityStatus({ active: false })).toBe('Inactive')
    })

    it('returns Unknown when no lastSeen and no active flag', () => {
      expect(store.getActivityStatus({})).toBe('Unknown')
    })

    it('returns Recently Active for projects seen within 7 days', () => {
      const lastSeen = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
      expect(store.getActivityStatus({ lastSeen })).toBe('Recently Active')
    })

    it('returns Stale for projects seen 8-30 days ago', () => {
      const lastSeen = new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
      expect(store.getActivityStatus({ lastSeen })).toBe('Stale')
    })

    it('returns Old for projects seen more than 30 days ago', () => {
      const lastSeen = new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString()
      expect(store.getActivityStatus({ lastSeen })).toBe('Old')
    })
  })

  describe('pagination methods', () => {
    beforeEach(() => {
      store.projects = Array.from({ length: 50 }, (_, i) =>
        makeProject({ uuid: String(i), name: `p-${i}` })
      )
      store.updatePaginationInfo()
    })

    it('goToPage changes currentPage within bounds', () => {
      store.goToPage(2)
      expect(store.currentPage).toBe(2)
    })

    it('goToPage ignores out-of-bound values', () => {
      store.goToPage(99)
      expect(store.currentPage).toBe(1)
    })

    it('nextPage advances page when not on last page', () => {
      store.currentPage = 1
      store.nextPage()
      expect(store.currentPage).toBe(2)
    })

    it('nextPage does not advance beyond last page', () => {
      store.currentPage = store.totalPages
      store.nextPage()
      expect(store.currentPage).toBe(store.totalPages)
    })

    it('previousPage moves back when not on first page', () => {
      store.currentPage = 2
      store.previousPage()
      expect(store.currentPage).toBe(1)
    })

    it('previousPage does not go below page 1', () => {
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
  })

  describe('filter methods', () => {
    it('setSearchQuery resets to page 1', () => {
      store.currentPage = 3
      store.setSearchQuery('alpha')
      expect(store.searchQuery).toBe('alpha')
      expect(store.currentPage).toBe(1)
    })

    it('setActiveFilter resets to page 1', () => {
      store.currentPage = 2
      store.setActiveFilter(true)
      expect(store.activeOnly).toBe(true)
      expect(store.currentPage).toBe(1)
    })

    it('clearFilters resets all filter state', () => {
      store.searchQuery = 'x'
      store.activeOnly = true
      store.selectedTags = ['tag-1']
      store.currentPage = 3
      store.clearFilters()
      expect(store.searchQuery).toBe('')
      expect(store.activeOnly).toBe(false)
      expect(store.selectedTags).toEqual([])
      expect(store.currentPage).toBe(1)
    })

    it('addTagFilter adds a tag and does not duplicate', () => {
      store.addTagFilter('sec')
      store.addTagFilter('sec')
      expect(store.selectedTags).toEqual(['sec'])
    })

    it('removeTagFilter removes an existing tag', () => {
      store.selectedTags = ['sec', 'ops']
      store.removeTagFilter('sec')
      expect(store.selectedTags).toEqual(['ops'])
    })
  })

  describe('loadProjects', () => {
    it('populates projects from the API response', async () => {
      const { default: axios } = await import('axios')
      const mockProjects = [makeProject({ uuid: 'abc', name: 'test' })]
      axios.get.mockResolvedValue({ data: mockProjects })

      await store.loadProjects()

      expect(store.projects).toEqual(mockProjects)
      expect(store.isLoading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('unwraps {data} envelope from API', async () => {
      const { default: axios } = await import('axios')
      const mockProjects = [makeProject()]
      axios.get.mockResolvedValue({ data: { data: mockProjects } })

      await store.loadProjects()

      expect(store.projects).toEqual(mockProjects)
    })

    it('sets error and empties projects on failure', async () => {
      const { default: axios } = await import('axios')
      axios.get.mockRejectedValue({ message: 'Network error' })

      await expect(store.loadProjects()).rejects.toBeTruthy()
      expect(store.projects).toEqual([])
      expect(store.error).toBeTruthy()
    })

    it('is a no-op while already loading', async () => {
      const { default: axios } = await import('axios')
      store.isLoading = true
      await store.loadProjects()
      expect(axios.get).not.toHaveBeenCalled()
    })
  })

  describe('getProjectById / getProjectByName', () => {
    beforeEach(() => {
      store.projects = [makeProject({ uuid: 'abc-123', name: 'alpha' })]
    })

    it('finds a project by uuid', () => {
      expect(store.getProjectById('abc-123')).toBeDefined()
    })

    it('returns undefined for unknown uuid', () => {
      expect(store.getProjectById('nope')).toBeUndefined()
    })

    it('finds a project by name', () => {
      expect(store.getProjectByName('alpha')).toBeDefined()
    })
  })

  describe('bulkDeleteProjects', () => {
    it('removes successfully deleted projects from local state', async () => {
      const { default: axios } = await import('axios')
      const uuids = ['uuid-1', 'uuid-2']
      store.projects = uuids.map(uuid => makeProject({ uuid }))

      axios.delete.mockResolvedValue({
        data: { results: { success: uuids, failed: [] } }
      })

      const result = await store.bulkDeleteProjects(uuids)

      expect(store.projects).toHaveLength(0)
      expect(result.success).toBe(2)
      expect(result.failed).toBe(0)
    })

    it('reports partial success when some deletions fail', async () => {
      const { default: axios } = await import('axios')
      const uuids = ['uuid-1', 'uuid-2']
      store.projects = uuids.map(uuid => makeProject({ uuid }))

      axios.delete.mockResolvedValue({
        data: {
          results: {
            success: ['uuid-1'],
            failed: [{ uuid: 'uuid-2', error: 'Not found' }]
          }
        }
      })

      const result = await store.bulkDeleteProjects(uuids)

      expect(store.projects).toHaveLength(1)
      expect(result.success).toBe(1)
      expect(result.failed).toBe(1)
      expect(store.error).toBeTruthy()
    })
  })

  describe('clearError / resetPagination / setPageSize', () => {
    it('clearError nullifies the error state', () => {
      store.error = 'something went wrong'
      store.clearError()
      expect(store.error).toBeNull()
    })

    it('resetPagination resets to page 1 and pageSize 20', () => {
      store.currentPage = 5
      store.pageSize = 100
      store.resetPagination()
      expect(store.currentPage).toBe(1)
      expect(store.pageSize).toBe(20)
    })

    it('setPageSize updates pageSize and resets to page 1', () => {
      store.currentPage = 3
      store.setPageSize(50)
      expect(store.pageSize).toBe(50)
      expect(store.currentPage).toBe(1)
    })
  })
})
