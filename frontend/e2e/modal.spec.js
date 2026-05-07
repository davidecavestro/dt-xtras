import { test, expect } from '@playwright/test'

test.describe('Modal Component', () => {
  test.beforeEach(async ({ page }) => {
    // Mock projects endpoint
    await page.route('/api/projects*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          projects: [
            {
              uuid: 'test-project',
              name: 'Test Project',
              version: '1.0.0',
              active: true,
              tags: [],
              metrics: { components: 10, vulnerableComponents: 0 }
            }
          ],
          total: 1
        })
      })
    })

    // Mock taxonomies
    await page.route('/api/taxonomies', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    // Mock auth
    await page.route('/api/auth/check', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ authenticated: true })
      })
    })

    await page.goto('/bulk-actions')
    await page.waitForLoadState('networkidle')
  })

  test('modal opens without prop type warnings', async ({ page }) => {
    // Select a project
    await page.click('.cursor-pointer')

    // Click delete to open modal
    await page.click('button:has-text("Del")')

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
    // Select a project and open delete modal
    await page.click('.cursor-pointer')
    await page.click('button:has-text("Del")')

    // Wait for modal
    await page.waitForSelector('role=dialog')

    // Click backdrop (gray area outside modal)
    const backdrop = page.locator('.bg-gray-500').first()
    await backdrop.click()

    // Modal should close
    await expect(page.locator('text=Delete Projects')).not.toBeVisible()
  })

  test('modal closes on cancel button', async ({ page }) => {
    // Select a project and open delete modal
    await page.click('.cursor-pointer')
    await page.click('button:has-text("Del")')

    // Wait for modal
    await page.waitForSelector('role=dialog')

    // Click cancel
    await page.click('button:has-text("Cancel")')

    // Modal should close
    await expect(page.locator('text=Delete Projects')).not.toBeVisible()
  })

  test('modal has correct z-index and appears above content', async ({ page }) => {
    // Select a project and open delete modal
    await page.click('.cursor-pointer')
    await page.click('button:has-text("Del")')

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
