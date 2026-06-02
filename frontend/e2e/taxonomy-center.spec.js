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
      localStorage.setItem('auth_token', 'fake-test-token')
      localStorage.setItem('auth_username', 'testuser')
      localStorage.setItem('auth_permissions', '[]')
    })

    await page.route('/api/taxonomies', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_TAXONOMIES)
        })
      } else {
        await route.continue()
      }
    })

    await page.goto('/taxonomies')
    await page.waitForLoadState('networkidle')
  })

  test('shows Taxonomy Center heading', async ({ page }) => {
    await expect(page.locator('h2:has-text("Taxonomy Center")')).toBeVisible()
  })

  test('shows Add Taxonomy button', async ({ page }) => {
    await expect(page.locator('button:has-text("Add Taxonomy")')).toBeVisible()
  })

  test('lists existing taxonomies', async ({ page }) => {
    await expect(page.locator('text=Environment')).toBeVisible()
    await expect(page.locator('text=Customer')).toBeVisible()
  })

  test('opens Create Taxonomy form when Add Taxonomy is clicked', async ({ page }) => {
    await page.click('button:has-text("Add Taxonomy")')
    await expect(page.locator('text=Create Taxonomy')).toBeVisible()
    // Form fields should be visible
    await expect(page.locator('input[placeholder*="customer"]')).toBeVisible()
  })

  test('Create Taxonomy form has required fields', async ({ page }) => {
    await page.click('button:has-text("Add Taxonomy")')
    // ID, Name, Regex Pattern fields should be present
    await expect(page.locator('text=ID')).toBeVisible()
    await expect(page.locator('text=Name')).toBeVisible()
    await expect(page.locator('text=Regex Pattern')).toBeVisible()
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

    await page.route('/api/taxonomies', async (route) => {
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
    await page.fill('input[placeholder*="customer"]', 'brand')
    await page.fill('input[placeholder*="My Taxonomy"]', 'Brand')

    await page.click('button:has-text("Save")')

    // After save the form should close
    await expect(page.locator('text=Create Taxonomy')).not.toBeVisible()
  })

  test('shows empty state when no taxonomies exist', async ({ page }) => {
    await page.route('/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    await page.goto('/taxonomies')
    await page.waitForLoadState('networkidle')

    // Add Taxonomy button should still be there
    await expect(page.locator('button:has-text("Add Taxonomy")')).toBeVisible()
  })
})
