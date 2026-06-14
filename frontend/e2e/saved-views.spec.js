import { test, expect } from '@playwright/test'

// Shared auth + config bootstrap (mirrors the other specs): freeze APP_CONFIG so
// route mocks for http://localhost:8000 intercept, and set an auth token.
const initAuth = async (page) => {
  await page.addInitScript(() => {
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
}

const PROJECTS = [
  {
    uuid: 'p1',
    name: 'Alpha Service',
    version: '1.0.0',
    active: true,
    lastBomImport: new Date().toISOString(),
    tags: [],
    metrics: { components: 10, vulnerableComponents: 0, critical: 0, high: 0, medium: 0, low: 0 }
  }
]

test.describe('Saved views — ProjectCenter URL sync', () => {
  test.beforeEach(async ({ page }) => {
    await initAuth(page)
    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: { 'X-Total-Count': '1', 'Access-Control-Expose-Headers': 'X-Total-Count' },
        body: JSON.stringify(PROJECTS)
      })
    })
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('http://localhost:8000/api/tag', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
  })

  test('restores search and table view from the URL', async ({ page }) => {
    await page.goto('/projects?q=alpha&view=table')
    await page.waitForLoadState('domcontentloaded')

    // Search box reflects the shared query…
    await expect(page.locator('input[placeholder="Search by project name..."]')).toHaveValue('alpha')
    // …and the table view (not the default deck) is rendered.
    await expect(page.locator('table')).toBeVisible()
  })

  test('writes view changes back into the URL', async ({ page }) => {
    await page.goto('/projects')
    await page.waitForLoadState('domcontentloaded')
    await page.waitForSelector('text=Alpha Service')

    // Switch to table view; the URL should gain view=table.
    await page.click('[title="Table view (sortable)"]')
    await expect(page).toHaveURL(/view=table/)
  })
})

test.describe('Saved views — Dashboard focused node', () => {
  test.beforeEach(async ({ page }) => {
    await initAuth(page)
    await page.route('http://localhost:8000/api/project*', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(PROJECTS) })
    })
    await page.route('http://localhost:8000/api/tag', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    await page.route('http://localhost:8000/api/taxonomies', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    })
    // Hierarchical tree (default mode) with one focusable node.
    const tree = {
      nodes: [],
      edges: [],
      tree: [{ id: 'brand:acme', name: 'acme', type: 'taxonomy', children: [], projectsCount: 1 }]
    }
    // Regex (not glob) so it matches both /api/tree and /api/tree/hierarchical
    // — a glob '*' would not cross the '/' before "hierarchical".
    await page.route(/\/api\/tree/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(tree) })
    })
  })

  test('focuses the node named in the URL once the tree loads', async ({ page }) => {
    await page.goto('/?node=brand:acme')
    await page.waitForLoadState('domcontentloaded')

    // The "Focusing on:" banner appears for the restored node.
    await expect(page.locator('text=Focusing on:')).toBeVisible()
    await expect(page.locator('span.font-mono', { hasText: 'acme' })).toBeVisible()
  })
})
