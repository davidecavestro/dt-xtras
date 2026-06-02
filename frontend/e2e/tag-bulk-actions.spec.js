import { test, expect } from '@playwright/test'

const MOCK_TAGS = [
  { name: 'env:prod', projects: [{ uuid: 'proj-1' }] },
  { name: 'env:staging', projects: [] },
  { name: 'customer:acme', projects: [{ uuid: 'proj-1' }, { uuid: 'proj-2' }] }
]

const MOCK_PROJECTS = [
  {
    uuid: 'proj-1',
    name: 'My App',
    version: '1.0.0',
    active: true,
    lastBomImport: new Date().toISOString(),
    tags: [{ name: 'env:prod', taxonomy: { name: 'env', color: '#42f057' } }],
    metrics: { components: 20, vulnerableComponents: 1, critical: 0, high: 1, medium: 0, low: 0 }
  },
  {
    uuid: 'proj-2',
    name: 'Backend Service',
    version: '2.1.0',
    active: true,
    lastBomImport: new Date().toISOString(),
    tags: [{ name: 'customer:acme', taxonomy: { name: 'customer', color: '#ff6600' } }],
    metrics: { components: 50, vulnerableComponents: 0, critical: 0, high: 0, medium: 0, low: 0 }
  }
]

test.describe('Tag Bulk Actions', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      // index.html has an inline script that sets window.APP_CONFIG to literal
      // "${BACKEND_API_URL}" (un-substituted by vite preview). Freeze it first so
      // axios.defaults.baseURL gets the real value and our route mocks intercept.
      const e2eConfig = {
        BACKEND_API_URL: 'http://localhost:8000',
        DT_API_URL: 'http://localhost:8080',
        DT_FRONTEND_URL: 'http://localhost:3000'
      }
      Object.defineProperty(window, 'APP_CONFIG', { get: () => e2eConfig, set: () => {}, configurable: true })
      localStorage.setItem('auth_token', 'fake-test-token')
      localStorage.setItem('auth_username', 'testuser')
      localStorage.setItem('auth_permissions', '[]')
    })

    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 'env', name: 'Environment', color: '#42f057', hierarchical: false, priority: 1, relations: [] },
          { id: 'customer', name: 'Customer', color: '#ff6600', hierarchical: false, priority: 2, relations: [] }
        ])
      })
    })

    await page.route('http://localhost:8000/api/tag', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_TAGS)
      })
    })

    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_PROJECTS)
      })
    })

    await page.goto('/tag-bulk-actions')
    await page.waitForLoadState('domcontentloaded')
  })

  test('shows Tag Bulk Actions heading', async ({ page }) => {
    await expect(page.locator('h1:has-text("Tag Bulk Actions")')).toBeVisible()
  })

  test('Link Selected and Unlink Selected buttons are disabled initially', async ({ page }) => {
    // 'Unlink Selected' contains 'link Selected' as a substring, so :has-text() would match
    // both buttons. getByRole with exact:true avoids the strict-mode violation.
    await expect(page.getByRole('button', { name: 'Link Selected', exact: true })).toBeDisabled()
    await expect(page.getByRole('button', { name: 'Unlink Selected', exact: true })).toBeDisabled()
  })

  test('shows tags list', async ({ page }) => {
    await page.waitForSelector('text=env:prod')
    // Use .first() — tag names can appear both in the tag list and in project-tag badges
    await expect(page.locator('text=env:prod').first()).toBeVisible()
    await expect(page.locator('text=env:staging').first()).toBeVisible()
    await expect(page.locator('text=customer:acme').first()).toBeVisible()
  })

  test('shows projects list', async ({ page }) => {
    await page.waitForSelector('text=My App')
    await expect(page.locator('text=My App')).toBeVisible()
    await expect(page.locator('text=Backend Service')).toBeVisible()
  })

  test('selecting a tag updates Selected Tags count', async ({ page }) => {
    await page.waitForSelector('text=env:prod')

    // Click the env:prod tag row to select it
    await page.locator('text=env:prod').first().click()

    // Selected Tags counter should show (1)
    await expect(page.locator('text=Selected Tags (1)')).toBeVisible()
  })

  test('enables Link Selected when both a tag and project are selected', async ({ page }) => {
    await page.waitForSelector('text=env:prod')
    await page.waitForSelector('text=My App')

    await page.locator('text=env:prod').first().click()
    await page.locator('text=My App').first().click()

    await expect(page.getByRole('button', { name: 'Link Selected', exact: true })).toBeEnabled()
    await expect(page.getByRole('button', { name: 'Unlink Selected', exact: true })).toBeEnabled()
  })

  test('link operation updates status after linking', async ({ page }) => {
    // The Link Selected button calls the API directly (no confirmation modal)
    await page.route('http://localhost:8000/api/v1/tag/**/project*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })

    await page.waitForSelector('text=env:prod')
    await page.waitForSelector('text=My App')

    await page.locator('text=env:prod').first().click()
    await page.locator('text=My App').first().click()

    await page.getByRole('button', { name: 'Link Selected', exact: true }).click()

    // After a successful link, a status message appears
    await expect(page.locator('text=Successfully linked')).toBeVisible()
  })

  test('shows refresh button', async ({ page }) => {
    await expect(page.locator('button:has-text("Refresh")')).toBeVisible()
  })
})
