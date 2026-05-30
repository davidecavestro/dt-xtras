import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'

vi.mock('axios', () => ({
  default: {
    defaults: {},
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
}))

vi.mock('../../config.js', () => ({
  getConfig: () => ({ BACKEND_API_URL: 'http://localhost:8000' })
}))

beforeEach(() => {
  globalThis.logger = { error: vi.fn(), info: vi.fn(), debug: vi.fn(), warn: vi.fn() }
  localStorage.clear()
  vi.clearAllMocks()
})

afterEach(() => {
  localStorage.clear()
})

describe('AuthService', () => {
  describe('isAuthenticated', () => {
    it('returns false when no token is stored', async () => {
      const { default: auth } = await import('../auth.js')
      auth.token = null
      expect(auth.isAuthenticated()).toBe(false)
    })

    it('returns true when a token is present', async () => {
      const { default: auth } = await import('../auth.js')
      auth.token = 'some-token'
      expect(auth.isAuthenticated()).toBe(true)
    })
  })

  describe('hasPermission', () => {
    it('returns true when the permission is in the list', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = ['VIEW_PORTFOLIO', 'PORTFOLIO_MANAGEMENT']
      expect(auth.hasPermission('VIEW_PORTFOLIO')).toBe(true)
    })

    it('returns false when the permission is absent', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = ['VIEW_PORTFOLIO']
      expect(auth.hasPermission('PORTFOLIO_MANAGEMENT')).toBe(false)
    })

    it('returns false for an empty permissions list', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = []
      expect(auth.hasPermission('VIEW_PORTFOLIO')).toBe(false)
    })
  })

  describe('hasAnyPermission', () => {
    it('returns true when at least one permission matches', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = ['VIEW_PORTFOLIO']
      expect(auth.hasAnyPermission(['ADMIN', 'VIEW_PORTFOLIO'])).toBe(true)
    })

    it('returns false when none of the given permissions are present', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = ['VIEW_PORTFOLIO']
      expect(auth.hasAnyPermission(['ADMIN', 'PORTFOLIO_MANAGEMENT'])).toBe(false)
    })
  })

  describe('getUsername / getPermissions', () => {
    it('returns the current username', async () => {
      const { default: auth } = await import('../auth.js')
      auth.username = 'alice'
      expect(auth.getUsername()).toBe('alice')
    })

    it('returns the current permissions array', async () => {
      const { default: auth } = await import('../auth.js')
      auth.permissions = ['VIEW_PORTFOLIO']
      expect(auth.getPermissions()).toEqual(['VIEW_PORTFOLIO'])
    })
  })

  describe('login', () => {
    it('stores token and permissions on successful login', async () => {
      axios.post.mockResolvedValue({
        data: {
          access_token: 'jwt-token-abc',
          username: 'bob',
          permissions: ['VIEW_PORTFOLIO']
        }
      })
      const { default: auth } = await import('../auth.js')

      const result = await auth.login('bob', 'pass')

      expect(result.success).toBe(true)
      expect(auth.token).toBe('jwt-token-abc')
      expect(auth.username).toBe('bob')
      expect(auth.permissions).toEqual(['VIEW_PORTFOLIO'])
      expect(localStorage.getItem('auth_token')).toBe('jwt-token-abc')
      expect(localStorage.getItem('auth_username')).toBe('bob')
    })

    it('returns failure when response has no access_token', async () => {
      axios.post.mockResolvedValue({ data: { error: 'Bad credentials' } })
      const { default: auth } = await import('../auth.js')

      const result = await auth.login('bad', 'creds')

      expect(result.success).toBe(false)
      expect(result.error).toBeTruthy()
    })

    it('returns failure on network error', async () => {
      axios.post.mockRejectedValue({
        response: { data: { detail: 'Unauthorized' } }
      })
      const { default: auth } = await import('../auth.js')

      const result = await auth.login('bob', 'wrong')

      expect(result.success).toBe(false)
      expect(result.error).toBe('Unauthorized')
    })
  })

  describe('logout', () => {
    it('clears token and localStorage on logout', async () => {
      axios.post.mockResolvedValue({})
      const { default: auth } = await import('../auth.js')
      auth.token = 'some-token'
      auth.username = 'alice'
      auth.permissions = ['VIEW_PORTFOLIO']
      localStorage.setItem('auth_token', 'some-token')

      await auth.logout()

      expect(auth.token).toBeNull()
      expect(auth.username).toBeNull()
      expect(auth.permissions).toEqual([])
      expect(localStorage.getItem('auth_token')).toBeNull()
    })

    it('still clears state even when logout endpoint fails', async () => {
      axios.post.mockRejectedValue(new Error('Network error'))
      const { default: auth } = await import('../auth.js')
      auth.token = 'some-token'

      await auth.logout()

      expect(auth.token).toBeNull()
    })
  })
})
