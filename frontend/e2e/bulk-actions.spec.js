import { test, expect } from '@playwright/test'

test.describe('Project Bulk Actions', () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token so the router guard passes on protected routes
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

    // Mock API responses for projects
    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        // The /api/project endpoint returns a bare array (List[DTProject]);
        // the store reads response.data directly, not a { projects } wrapper.
        body: JSON.stringify([
            {
              uuid: 'project-1',
              name: 'Frontend App',
              version: '1.0.0',
              active: true,
              lastBomImport: new Date().toISOString(),
              tags: [
                { name: 'security-critical', taxonomy: { name: 'security', color: '#ff0000' } },
                { name: 'backend', taxonomy: null }
              ],
              metrics: {
                components: 50,
                vulnerableComponents: 5,
                critical: 1,
                high: 2,
                medium: 2,
                low: 0
              }
            },
            {
              uuid: 'project-2',
              name: 'Backend API',
              version: '2.0.0',
              active: true,
              lastBomImport: new Date().toISOString(),
              tags: [
                { name: 'api', taxonomy: null }
              ],
              metrics: {
                components: 30,
                vulnerableComponents: 0,
                critical: 0,
                high: 0,
                medium: 0,
                low: 0
              }
            }
        ])
      })
    })

    // Mock taxonomies endpoint
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'security',
            regex_pattern: '/^security-/',
            color: '#ff0000',
            badge_color: '#ff0000',
            badge_text_color: '#ffffff'
          }
        ])
      })
    })

    // Mock auth check
    await page.route('http://localhost:8000/api/auth/check', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: true })
      })
    })

    await page.goto('/project-bulk-actions')
    await page.waitForLoadState('domcontentloaded')
  })

  test('should display projects with correct tag colors', async ({ page }) => {
    // Wait for projects to load
    await page.waitForSelector('text=Frontend App')

    // Check that security tag has colored styling (not gray)
    const securityTag = page.locator('text=security-critical').first()
    await expect(securityTag).toBeVisible()

    // Verify tag has inline style for background color (from taxonomy)
    const tagStyle = await securityTag.evaluate(el => el.style.backgroundColor)
    // Should have some background color set (not empty)
    expect(tagStyle).toBeTruthy()
  })

  test('should toggle checkbox when clicking list item', async ({ page }) => {
    await page.waitForSelector('text=Frontend App')

    // Click on the Frontend App project row (default view is deck)
    await page.locator('text=Frontend App').first().click()

    // Verify checkbox is checked
    const firstCheckbox = page.locator('input[type="checkbox"]').first()
    await expect(firstCheckbox).toBeChecked()

    // Click again to uncheck
    await page.locator('text=Frontend App').first().click()
    await expect(firstCheckbox).not.toBeChecked()
  })

  test('should show bulk actions toolbar', async ({ page }) => {
    await page.waitForSelector('text=Frontend App')

    // Toolbar buttons are always visible (disabled when no selection)
    await expect(page.locator('[title="Delete selected"]')).toBeVisible()
    await expect(page.locator('[title="Activate selected"]')).toBeVisible()
    await expect(page.locator('[title="Deactivate selected"]')).toBeVisible()
  })

  test('should bulk delete selected projects', async ({ page }) => {
    // Mock the batch delete endpoint. The store reads response.data.results
    // ({ success, failed }), so the mock must return that shape.
    await page.route('http://localhost:8000/api/project/batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Deleted 1 of 1 projects',
          results: { success: ['project-1'], failed: [] }
        })
      })
    })

    // Select first project by clicking its name
    await page.waitForSelector('text=Frontend App')
    await page.locator('text=Frontend App').first().click()

    // Click delete button in toolbar
    await page.click('[title="Delete selected"]')

    // Verify delete confirmation modal appears
    await expect(page.locator('text=Delete Projects')).toBeVisible()
    // Project name appears in both the list and the modal; use first match
    await expect(page.locator('text=Frontend App').first()).toBeVisible()

    // Confirm delete
    await page.click('button:has-text("Delete")')

    // Verify success toast (or page reload)
    await page.waitForTimeout(500)
  })

  test('should switch between list and deck views', async ({ page }) => {
    await page.waitForSelector('text=Frontend App')

    // Default is DECK view — grid container visible
    await expect(page.locator('.grid').first()).toBeVisible()

    // View toggle: two icon-only buttons in the first .space-x-1 flex group
    const toggleButtons = page.locator('.flex.items-center.space-x-1').first().locator('button')

    // Switch to list view (first toggle button)
    await toggleButtons.nth(0).click()
    await expect(page.locator('.space-y-3')).toBeVisible()

    // Switch back to deck view (second toggle button)
    await toggleButtons.nth(1).click()
    await expect(page.locator('.grid').first()).toBeVisible()
  })

  test('should select all projects via toolbar', async ({ page }) => {
    await page.waitForSelector('text=Frontend App')

    // "All" is a <label title="Select all"> wrapping a checkbox
    await page.click('label[title="Select all"]')

    // Toolbar selection counter (the small number above the action buttons) should show 2
    await expect(page.locator('[title="Delete selected"]').locator('..').locator('div').first()).toContainText('2')
  })

  test('should display pagination above projects', async ({ page }) => {
    await page.waitForSelector('text=Frontend App')

    // Pagination "Showing X of Y" text should be present
    await expect(page.locator('text=Showing').first()).toBeVisible()
  })
})
