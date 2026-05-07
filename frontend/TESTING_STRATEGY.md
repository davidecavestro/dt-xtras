# Frontend Testing Strategy

## Problem Statement
Recent changes have caused regressions in:
- Tag badge colors (taxonomy styling)
- Modal icon prop types
- Layout structure (sticky positioning)
- Event handling (checkbox toggling)

## Testing Layers

### 1. Unit Tests (Vitest)
**Scope:** Store methods, utility functions, composables
**Files:**
- `src/stores/__tests__/projects.test.js` - CRUD operations, bulk actions
- `src/stores/__tests__/taxonomies.test.js` - Tag styling logic
- `src/utils/__tests__/taxonomyParser.test.js` - Regex handling
- `src/composables/__tests__/useToast.test.js` - Toast notifications

**Critical Tests:**
```javascript
// Tag styling logic - the most broken feature
describe('getTagStyle', () => {
  it('returns taxonomy colors for matching tags', () => {
    // Prevents gray badges when taxonomy exists
  })
  it('handles both string and object tags', () => {
    // Defensive programming
  })
  it('caches taxonomy lookup results', () => {
    // Performance
  })
})
```

### 2. Component Tests (Vue Test Utils + Vitest)
**Scope:** Individual component rendering and interaction
**Files:**
- `src/components/__tests__/ProjectBulkActions.test.js`
- `src/components/__tests__/ProjectCard.test.js`
- `src/components/__tests__/Modal.test.js`

**Critical Tests:**
```javascript
describe('ProjectBulkActions', () => {
  it('toggles checkbox when clicking list item', () => {
    // Uniform behavior between list/deck views
  })
  it('renders tag badges with taxonomy colors', () => {
    // Visual regression prevention
  })
  it('shows fixed toolbar on scroll', () => {
    // Layout stability
  })
})

describe('Modal', () => {
  it('accepts Function type for icon prop', () => {
    // Vue warning prevention
  })
})
```

### 3. E2E Tests (Playwright)
**Scope:** Full user workflows across pages
**Files:**
- `e2e/bulk-actions.spec.js`
- `e2e/tag-management.spec.js`
- `e2e/navigation.spec.js`

**Critical Paths:**
```javascript
test('bulk delete workflow', async () => {
  // 1. Navigate to bulk actions
  // 2. Select projects via click
  // 3. Click delete in toolbar
  // 4. Confirm in modal
  // 5. Verify projects removed
})

test('tag colors persist across view modes', async () => {
  // 1. View projects in list mode
  // 2. Verify tag colors
  // 3. Switch to deck mode
  // 4. Verify same tag colors
})
```

### 4. Visual Regression Tests (Chromatic/Storybook)
**Scope:** Component screenshots in isolation
**Files:**
- `src/components/__stories__/ProjectCard.stories.js`
- `src/components/__stories__/Modal.stories.js`

## Implementation Plan

### Phase 1: Foundation ✅ COMPLETE
1. ~~Install Vitest + Vue Test Utils~~ (Already configured)
2. ~~Install Playwright~~ (`npm install -D @playwright/test`)
3. ~~Configure test scripts in package.json~~ (Added `test:e2e`, `test:e2e:headed`, etc.)
4. ~~Write critical unit tests~~ (`src/stores/__tests__/taxonomies.test.js`, `src/components/__tests__/Modal.test.js`)

### Phase 2: Component Coverage ✅ COMPLETE
1. ~~Mount ProjectBulkActions with Pinia store~~ (`src/components/__tests__/ProjectBulkActions.test.js`)
2. ~~Test checkbox toggle behavior~~ (E2E test covers this)
3. ~~Test tag color rendering~~ (Unit + E2E tests cover this)
4. ~~Test modal interactions~~ (Modal.test.js covers this)

### Phase 3: E2E Coverage ✅ COMPLETE
1. ~~Set up Playwright with auth mocking~~ (`playwright.config.js` with route mocking)
2. ~~Write critical path tests~~ (`e2e/bulk-actions.spec.js`, `e2e/modal.spec.js`)
3. Configure CI to run on PR (When ready)

### Phase 4: Visual Tests (Future)
1. Set up Storybook
2. Create stories for key components
3. Integrate Chromatic

## Running Tests

### Development Time (Daily Use)

```bash
cd /workspace/frontend

# Run dev server (terminal 1)
npm run dev

# Quick unit tests in watch mode (terminal 2)
npm run test

# Or run unit tests once
npm run test:run

# For E2E tests:
# 1. Build and start preview server (terminal 1)
npm run build && npm run preview -- --port 4173 --host

# 2. Run E2E tests (terminal 2)
npm run test:e2e           # Headless
npm run test:e2e:headed    # See browser
npm run test:e2e:ui        # Interactive debugger
npm run test:e2e:debug     # Full debug mode

# Run all tests at once (requires build + preview running)
npm run test:all:local
```

### CI Time (Automated)

```bash
cd /workspace/frontend

# Unit tests with coverage (one shot, no watch)
npm run test:ci

# Full E2E test suite (builds, starts server, tests, cleanup)
npm run test:e2e:ci

# Run everything (unit + e2e) - full CI pipeline
npm run test:all
```

**Quick Reference:**
| Script | Use Case |
|--------|----------|
| `npm run test` | Dev - unit tests in watch mode |
| `npm run test:run` | Dev - unit tests once |
| `npm run test:ci` | CI - unit tests with coverage |
| `npm run test:e2e` | Dev - E2E (needs preview server) |
| `npm run test:e2e:ci` | CI - E2E with auto server |
| `npm run test:all:local` | Dev - all tests (needs server) |
| `npm run test:all` | CI - complete test suite |

### E2E Test Configuration

Playwright is configured to:
- Mock API responses (no backend needed for tests)
- Use Chromium by default
- Reuse existing server (won't try to start new one)
- Capture screenshots/videos on failure
- Generate HTML reports

### Viewing Test Results

```bash
# After running tests, view HTML report
npx playwright show-report

# Or open directly
open playwright-report/index.html
```

### Troubleshooting

**Timeout waiting for webServer:**
- Make sure you've built the app: `npm run build`
- Start preview server manually: `npm run preview -- --port 4173 --host`
- Then run tests in another terminal

**Port already in use:**
- Kill existing process: `kill $(lsof -t -i:4173)`
- Or use different port: `PORT=4174 npm run preview` + `PLAYWRIGHT_BASE_URL=http://localhost:4174 npm run test:e2e`

**Browser launch errors in DevContainer:**
If you see `error while loading shared libraries: libatk-1.0.so.0`:

1. **Quick fix - install dependencies:**
   ```bash
   ./scripts/install-playwright-deps.sh
   ```

2. **Or rebuild devcontainer** with Playwright deps in Dockerfile:
   ```dockerfile
   RUN apt-get update && apt-get install -y \
     libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
     libcups2 libdrm2 libxcomposite1 libxdamage1 \
     libxfixes3 libxrandr2 libgbm1 libxkbcommon0 \
     libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0
   ```

3. **Alternative - run E2E outside devcontainer:**
   ```bash
   # On host machine
   cd frontend
   npm run test:e2e:headed
   ```

**HTML report server hangs:**
The Playwright report server can hang in some environments. Use:
```bash
# Instead of npx playwright show-report
open playwright-report/index.html  # macOS
xdg-open playwright-report/index.html  # Linux
# Or just open the file directly in browser
```

## CI Integration

Tests run on:
- Every PR (blocking merge)
- Main branch merges
- Nightly (full E2E suite)

## Success Metrics

- 80% code coverage for stores
- 100% coverage for tag styling logic
- All critical paths covered by E2E
- Zero visual regressions in Chromatic

## Regression Prevention Checklist

Before any PR is merged:
- [ ] Unit tests pass
- [ ] Component tests pass
- [ ] E2E tests pass
- [ ] No visual diffs in Chromatic
- [ ] Manual QA on changed features
