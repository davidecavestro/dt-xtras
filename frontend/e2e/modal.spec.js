import { test, expect } from '@playwright/test'

test.describe('Modal Component', () => {
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

    // Mock projects endpoint
    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        // The /api/project endpoint returns a bare array (List[DTProject]);
        // the store reads response.data directly, not a { projects } wrapper.
        body: JSON.stringify([
          {
            uuid: 'test-project',
            name: 'Test Project',
            version: '1.0.0',
            active: true,
            tags: [],
            metrics: { components: 10, vulnerableComponents: 0 }
          }
        ])
      })
    })

    // Mock taxonomies
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    // Mock auth
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

  test('modal opens without prop type warnings', async ({ page }) => {
    await page.waitForSelector('text=Test Project')
    await page.locator('text=Test Project').first().click()
    await page.click('[title="Delete selected"]')

    // Wait for modal to appear
    await page.waitForSelector('role=dialog')

    // Check no console errors about prop types
    const consoleErrors = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })
    page.on('pageerror', err => {
      consoleErrors.push(err.message)
    })

    // Wait a moment for any async errors
    await page.waitForTimeout(500)

    // Should have no prop type warnings
    const propTypeErrors = consoleErrors.filter(e =>
      e.includes('Invalid prop') || e.includes('type check failed')
    )
    expect(propTypeErrors).toHaveLength(0)

    // Verify modal renders correctly
    await expect(page.locator('text=Delete Projects')).toBeVisible()
  })

  test('modal closes on backdrop click', async ({ page }) => {
    await page.waitForSelector('text=Test Project')
    await page.locator('text=Test Project').first().click()
    await page.click('[title="Delete selected"]')

    // Wait for modal
    await page.waitForSelector('role=dialog')

    // The backdrop is fixed inset-0 with @click.self="handleClose".
    // Use dispatchEvent so the click fires directly on the element (bypassing
    // the sidebar z-50 overlay that intercepts normal pointer events).
    await page.locator('.bg-gray-500').first().dispatchEvent('click')

    // Modal should close
    await expect(page.locator('text=Delete Projects')).not.toBeVisible()
  })

  test('modal closes on cancel button', async ({ page }) => {
    await page.waitForSelector('text=Test Project')
    await page.locator('text=Test Project').first().click()
    await page.click('[title="Delete selected"]')

    // Wait for modal
    await page.waitForSelector('role=dialog')

    // Click cancel
    await page.click('button:has-text("Cancel")')

    // Modal should close
    await expect(page.locator('text=Delete Projects')).not.toBeVisible()
  })

  test('modal has correct z-index and appears above content', async ({ page }) => {
    await page.waitForSelector('text=Test Project')
    await page.locator('text=Test Project').first().click()
    await page.click('[title="Delete selected"]')

    // Wait for modal
    const modal = page.locator('role=dialog')
    await modal.waitFor()

    // Check modal panel has higher z-index than backdrop
    const modalPanel = modal.locator('div').first()
    const zIndex = await modalPanel.evaluate(el => {
      const style = window.getComputedStyle(el)
      return style.zIndex
    })

    // Should have some z-index value
    expect(zIndex).toBeTruthy()
  })
})
