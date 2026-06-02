import { test, expect } from '@playwright/test'

// Auth endpoint uses the absolute BACKEND_API_URL (defaults to http://localhost:8000 in
// the built app when no window.APP_CONFIG is present).
const AUTH_LOGIN_PATTERN = '**/auth/login'

test.describe('Login', () => {
  test('unauthenticated user is redirected to /login', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/\/login/)
    await expect(page.locator('h2')).toContainText('Sign in to dt-xtras')
  })

  test('login form renders correctly', async ({ page }) => {
    await page.goto('/login')
    await expect(page.locator('h2')).toContainText('Sign in to dt-xtras')
    await expect(page.locator('input[name="username"]')).toBeVisible()
    await expect(page.locator('input[name="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toContainText('Sign in')
  })

  test('shows error message on invalid credentials', async ({ page }) => {
    // Use 400 not 401: a 401 triggers the axios response interceptor which calls
    // window.location.href = '/login', navigating away before the error can render.
    await page.route(AUTH_LOGIN_PATTERN, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' })
      })
    })

    await page.goto('/login')
    await page.fill('input[name="username"]', 'wronguser')
    await page.fill('input[name="password"]', 'wrongpass')
    await page.click('button[type="submit"]')

    await expect(page.locator('text=Authentication failed')).toBeVisible()
    await expect(page.locator('text=Invalid credentials')).toBeVisible()
  })

  test('successful login redirects to dashboard', async ({ page }) => {
    await page.route(AUTH_LOGIN_PATTERN, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'fake-jwt-token',
          username: 'admin',
          permissions: []
        })
      })
    })

    // Mock dashboard data so the page loads without network errors
    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('http://localhost:8000/api/tag', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('http://localhost:8000/api/tree*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ nodes: [], edges: [], tree: [] })
      })
    })

    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')

    await expect(page).toHaveURL('/')
    await expect(page.locator('h2:has-text("Security Dashboard")')).toBeVisible()
  })

  test('submit button is disabled while login is in progress', async ({ page }) => {
    // Delay the response to observe the loading state
    await page.route(AUTH_LOGIN_PATTERN, async (route) => {
      await new Promise(resolve => setTimeout(resolve, 300))
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' })
      })
    })

    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'password')
    await page.click('button[type="submit"]')

    // Button should be disabled while waiting
    await expect(page.locator('button[type="submit"]')).toBeDisabled()
  })
})
