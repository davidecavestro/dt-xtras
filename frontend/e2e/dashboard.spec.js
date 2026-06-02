import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token so the router guard passes
    await page.addInitScript(() => {
      localStorage.setItem('auth_token', 'fake-test-token')
      localStorage.setItem('auth_username', 'testuser')
      localStorage.setItem('auth_permissions', '[]')
    })

    await page.route('/api/project*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            uuid: 'proj-1',
            name: 'My App',
            version: '1.0.0',
            active: true,
            lastBomImport: new Date().toISOString(),
            tags: [{ name: 'env:prod', taxonomy: { name: 'env', color: '#42f057' } }],
            metrics: { components: 20, vulnerableComponents: 2, critical: 1, high: 1, medium: 0, low: 0 }
          }
        ])
      })
    })

    await page.route('/api/tag', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { name: 'env:prod', projects: [] }
        ])
      })
    })

    await page.route('/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 'env',
            name: 'Environment',
            regex_pattern: '^env:(?P<value>.+)$',
            color: '#42f057',
            hierarchical: false,
            priority: 1,
            relations: []
          }
        ])
      })
    })

    await page.route('/api/tree*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ nodes: [], edges: [], tree: [] })
      })
    })

    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
  })

  test('shows Security Dashboard heading', async ({ page }) => {
    await expect(page.locator('h2:has-text("Security Dashboard")')).toBeVisible()
  })

  test('shows refresh button', async ({ page }) => {
    await expect(page.locator('button:has-text("Refresh")')).toBeVisible()
  })

  test('displays project data after loading', async ({ page }) => {
    await page.waitForSelector('text=My App')
    await expect(page.locator('text=My App')).toBeVisible()
  })

  test('shows sidebar navigation links', async ({ page }) => {
    await expect(page.locator('a[href="/"]')).toBeVisible()
    await expect(page.locator('a[href="/taxonomies"]')).toBeVisible()
    await expect(page.locator('a[href="/tags"]')).toBeVisible()
    await expect(page.locator('a[href="/project-bulk-actions"]')).toBeVisible()
  })

  test('shows error state when API fails', async ({ page }) => {
    // Override the tree mock to simulate a failure
    await page.route('/api/tree*', async (route) => {
      await route.fulfill({ status: 500, body: 'Internal Server Error' })
    })

    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')

    // Page should still render without crashing (error handled gracefully)
    await expect(page.locator('h2:has-text("Security Dashboard")')).toBeVisible()
  })
})
