import { describe, it, expect, vi, beforeAll } from 'vitest'
import { usePagination } from '../usePagination.js'

beforeAll(() => {
  globalThis.logger = { error: vi.fn(), info: vi.fn(), debug: vi.fn(), warn: vi.fn() }
})

describe('usePagination', () => {
  describe('initial state', () => {
    it('defaults to page 1 and pageSize 20', () => {
      const pager = usePagination()
      expect(pager.currentPage).toBe(1)
      expect(pager.pageSize).toBe(20)
    })

    it('respects custom initial values', () => {
      const pager = usePagination({ initialPage: 3, initialPageSize: 50 })
      expect(pager.currentPage).toBe(3)
      expect(pager.pageSize).toBe(50)
    })

    it('starts with zero totalItems and totalPages', () => {
      const pager = usePagination()
      expect(pager.totalItems).toBe(0)
      expect(pager.totalPages).toBe(0)
    })

    it('exposes the configured pageSizeOptions', () => {
      const pager = usePagination({ pageSizeOptions: [5, 10] })
      expect(pager.pageSizeOptions).toEqual([5, 10])
    })
  })

  describe('computed: startItem / endItem', () => {
    it('startItem is 0 when totalItems is 0', () => {
      const pager = usePagination()
      expect(pager.startItem).toBe(0)
    })

    it('startItem is 1 on the first page', () => {
      const pager = usePagination()
      pager.totalItems = 100
      pager.totalPages = 5
      expect(pager.startItem).toBe(1)
    })

    it('startItem is 21 on page 2 with pageSize 20', () => {
      const pager = usePagination()
      pager.totalItems = 100
      pager.totalPages = 5
      pager.currentPage = 2
      expect(pager.startItem).toBe(21)
    })

    it('endItem does not exceed totalItems', () => {
      const pager = usePagination()
      pager.totalItems = 25
      pager.totalPages = 2
      pager.currentPage = 2
      expect(pager.endItem).toBe(25)
    })
  })

  describe('computed: hasNextPage / hasPreviousPage', () => {
    it('hasNextPage is false when on the last page', () => {
      const pager = usePagination()
      pager.totalPages = 3
      pager.currentPage = 3
      expect(pager.hasNextPage).toBe(false)
    })

    it('hasNextPage is true when there are more pages', () => {
      const pager = usePagination()
      pager.totalPages = 3
      pager.currentPage = 1
      expect(pager.hasNextPage).toBe(true)
    })

    it('hasPreviousPage is false on the first page', () => {
      const pager = usePagination()
      expect(pager.hasPreviousPage).toBe(false)
    })

    it('hasPreviousPage is true when beyond the first page', () => {
      const pager = usePagination()
      pager.currentPage = 2
      expect(pager.hasPreviousPage).toBe(true)
    })
  })

  describe('setPage', () => {
    it('moves to the given page when within bounds', () => {
      const pager = usePagination()
      pager.totalPages = 5
      pager.setPage(3)
      expect(pager.currentPage).toBe(3)
    })

    it('does not move below page 1', () => {
      const pager = usePagination()
      pager.totalPages = 5
      pager.setPage(0)
      expect(pager.currentPage).toBe(1)
    })

    it('does not move beyond totalPages', () => {
      const pager = usePagination()
      pager.totalPages = 3
      pager.setPage(10)
      expect(pager.currentPage).toBe(1)
    })
  })

  describe('setPageSize', () => {
    it('updates pageSize and resets to page 1', () => {
      const pager = usePagination()
      pager.currentPage = 3
      pager.setPageSize(50)
      expect(pager.pageSize).toBe(50)
      expect(pager.currentPage).toBe(1)
    })

    it('ignores values not in pageSizeOptions', () => {
      const pager = usePagination({ pageSizeOptions: [10, 20, 50] })
      pager.setPageSize(99)
      expect(pager.pageSize).toBe(20)
    })
  })

  describe('nextPage / previousPage', () => {
    it('nextPage increments page', () => {
      const pager = usePagination()
      pager.totalPages = 5
      pager.currentPage = 2
      pager.nextPage()
      expect(pager.currentPage).toBe(3)
    })

    it('nextPage is a no-op on the last page', () => {
      const pager = usePagination()
      pager.totalPages = 3
      pager.currentPage = 3
      pager.nextPage()
      expect(pager.currentPage).toBe(3)
    })

    it('previousPage decrements page', () => {
      const pager = usePagination()
      pager.totalPages = 5
      pager.currentPage = 3
      pager.previousPage()
      expect(pager.currentPage).toBe(2)
    })

    it('previousPage is a no-op on page 1', () => {
      const pager = usePagination()
      pager.previousPage()
      expect(pager.currentPage).toBe(1)
    })
  })

  describe('firstPage / lastPage', () => {
    it('firstPage resets to page 1', () => {
      const pager = usePagination()
      pager.currentPage = 4
      pager.firstPage()
      expect(pager.currentPage).toBe(1)
    })

    it('lastPage jumps to totalPages', () => {
      const pager = usePagination()
      pager.totalPages = 7
      pager.lastPage()
      expect(pager.currentPage).toBe(7)
    })
  })

  describe('updatePaginationMetadata', () => {
    it('updates currentPage from metadata', () => {
      const pager = usePagination()
      pager.updatePaginationMetadata({ currentPage: 3 })
      expect(pager.currentPage).toBe(3)
    })

    it('updates pageSize from metadata', () => {
      const pager = usePagination()
      pager.updatePaginationMetadata({ pageSize: 50 })
      expect(pager.pageSize).toBe(50)
    })

    it('updates totalItems from metadata', () => {
      const pager = usePagination()
      pager.updatePaginationMetadata({ totalItems: 200 })
      expect(pager.totalItems).toBe(200)
    })

    it('updates totalPages from metadata', () => {
      const pager = usePagination()
      pager.updatePaginationMetadata({ totalPages: 10 })
      expect(pager.totalPages).toBe(10)
    })

    it('calculates totalPages from totalItems and pageSize when totalPages is absent', () => {
      const pager = usePagination()
      pager.updatePaginationMetadata({ totalItems: 45, pageSize: 10 })
      expect(pager.totalPages).toBe(5)
    })
  })

  describe('reset', () => {
    it('restores all values to initial defaults', () => {
      const pager = usePagination({ initialPage: 1, initialPageSize: 20 })
      pager.currentPage = 5
      pager.totalItems = 999
      pager.error = 'oops'

      pager.reset()

      expect(pager.currentPage).toBe(1)
      expect(pager.pageSize).toBe(20)
      expect(pager.totalItems).toBe(0)
      expect(pager.totalPages).toBe(0)
      expect(pager.error).toBeNull()
    })
  })

  describe('setLoading / setError / clearError', () => {
    it('setLoading toggles the loading flag', () => {
      const pager = usePagination()
      pager.setLoading(true)
      expect(pager.loading).toBe(true)
      pager.setLoading(false)
      expect(pager.loading).toBe(false)
    })

    it('setError stores the error message', () => {
      const pager = usePagination()
      pager.setError('Network timeout')
      expect(pager.error).toBe('Network timeout')
    })

    it('clearError nullifies the error', () => {
      const pager = usePagination()
      pager.setError('boom')
      pager.clearError()
      expect(pager.error).toBeNull()
    })
  })
})
