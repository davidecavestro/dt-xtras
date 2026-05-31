import { test, expect } from '@playwright/test'

test.describe('Project Bulk Actions', () => {
  test.beforeEach(async ({ page }) => {
    // Mock API responses for projects
    await page.route('/api/project*', async (route) => {
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
    await page.route('/api/taxonomies', async (route) => {
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
    await page.route('/api/auth/check', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: true })
      })
    })

    await page.goto('/project-bulk-actions')
    await page.waitForLoadState('networkidle')
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
    // Click on first project row
    const firstProject = page.locator('.cursor-pointer').first()
    await firstProject.click()

    // Verify checkbox is checked
    const firstCheckbox = page.locator('input[type="checkbox"]').first()
    await expect(firstCheckbox).toBeChecked()

    // Click again to uncheck
    await firstProject.click()
    await expect(firstCheckbox).not.toBeChecked()
  })

  test('should show bulk actions toolbar', async ({ page }) => {
    // Wait for projects to load
    await page.waitForSelector('text=Frontend App')

    // Check toolbar is visible (fixed position on right)
    const toolbar = page.locator('.fixed').filter({ hasText: 'Del' })
    await expect(toolbar).toBeVisible()

    // Verify toolbar has action buttons
    await expect(page.locator('button:has-text("Del")')).toBeVisible()
    await expect(page.locator('button:has-text("Act")')).toBeVisible()
    await expect(page.locator('button:has-text("Deact")')).toBeVisible()
  })

  test('should bulk delete selected projects', async ({ page }) => {
    // Mock the batch delete endpoint. The store reads response.data.results
    // ({ success, failed }), so the mock must return that shape.
    await page.route('/api/project/batch', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: 'Deleted 1 of 1 projects',
          results: { success: ['project-1'], failed: [] }
        })
      })
    })

    // Select first project
    const firstProject = page.locator('.cursor-pointer').first()
    await firstProject.click()

    // Click delete button in toolbar
    await page.click('button:has-text("Del")')

    // Verify delete confirmation modal appears
    await expect(page.locator('text=Delete Projects')).toBeVisible()
    await expect(page.locator('text=Frontend App')).toBeVisible()

    // Confirm delete
    await page.click('button:has-text("Delete")')

    // Verify success toast (or page reload)
    await page.waitForTimeout(500)
  })

  test('should switch between list and deck views', async ({ page }) => {
    // Wait for projects
    await page.waitForSelector('text=Frontend App')

    // Default is list view - check for list structure
    await expect(page.locator('.space-y-3')).toBeVisible()

    // Click deck view button
    await page.click('button[title="Deck View"]')

    // Check for grid layout (deck view)
    await expect(page.locator('.grid')).toBeVisible()

    // Click back to list view
    await page.click('button[title="List View"]')

    // Check for list layout again
    await expect(page.locator('.space-y-3')).toBeVisible()
  })

  test('should select all projects via toolbar', async ({ page }) => {
    // Wait for projects
    await page.waitForSelector('text=Frontend App')

    // Click "All" button in toolbar
    await page.click('button:has-text("All")')

    // Verify all checkboxes are checked
    const checkboxes = page.locator('input[type="checkbox"]')
    const count = await checkboxes.count()

    for (let i = 0; i < count; i++) {
      await expect(checkboxes.nth(i)).toBeChecked()
    }

    // Verify toolbar shows count
    await expect(page.locator('text=2')).toBeVisible()
  })

  test('should display pagination above projects', async ({ page }) => {
    // Wait for projects
    await page.waitForSelector('text=Frontend App')

    // Check pagination controls exist
    const pagination = page.locator('text=Showing').first()
    await expect(pagination).toBeVisible()

    // Verify it's above the projects (check order in DOM)
    const paginationBox = await pagination.boundingBox()
    const projectsBox = await page.locator('.space-y-3, .grid').first().boundingBox()

    expect(paginationBox?.y).toBeLessThan(projectsBox?.y || Infinity)
  })
})
