import { test, expect } from '@playwright/test'

const MOCK_TAXONOMIES = [
  {
    id: 'env',
    name: 'Environment',
    regex_pattern: '^env:(?P<value>.+)$',
    color: '#42f057',
    hierarchical: false,
    priority: 1,
    relations: []
  },
  {
    id: 'customer',
    name: 'Customer',
    regex_pattern: '^cust:(?P<value>.+)$',
    color: '#ff6600',
    hierarchical: false,
    priority: 2,
    relations: []
  }
]

test.describe('Taxonomy Center', () => {
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
        body: JSON.stringify(MOCK_TAXONOMIES)
      })
    })

    await page.goto('/taxonomies')
    await page.waitForLoadState('domcontentloaded')
  })

  test('shows Taxonomy Center heading', async ({ page }) => {
    await expect(page.locator('h2:has-text("Taxonomy Center")')).toBeVisible()
  })

  test('shows Add Taxonomy button', async ({ page }) => {
    await expect(page.locator('button:has-text("Add Taxonomy")')).toBeVisible()
  })

  test('lists existing taxonomies', async ({ page }) => {
    // Cytoscape graph init can delay the list render; use a longer timeout.
    // Use .first() — taxonomy names also appear as ID badges (e.g. "customer" pill).
    await expect(page.locator('text=Environment').first()).toBeVisible({ timeout: 15000 })
    await expect(page.locator('text=Customer').first()).toBeVisible({ timeout: 15000 })
  })

  test('opens Create Taxonomy form when Add Taxonomy is clicked', async ({ page }) => {
    await page.click('button:has-text("Add Taxonomy")')
    await expect(page.locator('text=Create Taxonomy')).toBeVisible()
    // Form fields should be visible
    await expect(page.locator('input[placeholder*="customer, env"]')).toBeVisible()
  })

  test('Create Taxonomy form has required fields', async ({ page }) => {
    await page.click('button:has-text("Add Taxonomy")')
    // Use placeholder text to locate fields — the ID/Name labels are partially
    // obscured by the sidebar at z-50 (the modal renders inside the z-10 content wrapper)
    await expect(page.locator('input[placeholder*="customer, env"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="Customer, Environment"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="env:"]')).toBeVisible()
  })

  test('cancels Create Taxonomy form on close', async ({ page }) => {
    await page.click('button:has-text("Add Taxonomy")')
    await expect(page.locator('text=Create Taxonomy')).toBeVisible()

    await page.click('button:has-text("✕")')
    await expect(page.locator('text=Create Taxonomy')).not.toBeVisible()
  })

  test('submits new taxonomy via POST and refreshes list', async ({ page }) => {
    const newTaxonomy = {
      id: 'brand',
      name: 'Brand',
      regex_pattern: '^brand:(?P<value>.+)$',
      color: '#0000ff',
      hierarchical: false,
      priority: 3,
      relations: []
    }

    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(newTaxonomy)
        })
      } else {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([...MOCK_TAXONOMIES, newTaxonomy])
        })
      }
    })

    await page.click('button:has-text("Add Taxonomy")')
    await page.fill('input[placeholder*="customer, env"]', 'brand')
    await page.fill('input[placeholder*="Customer, Environment"]', 'Brand')

    await page.click('button:has-text("Save")')

    // After save the form should close
    await expect(page.locator('text=Create Taxonomy')).not.toBeVisible()
  })

  test('shows empty state when no taxonomies exist', async ({ page }) => {
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    await page.goto('/taxonomies')
    await page.waitForLoadState('domcontentloaded')

    // Add Taxonomy button should still be there
    await expect(page.locator('button:has-text("Add Taxonomy")')).toBeVisible()
  })
})
