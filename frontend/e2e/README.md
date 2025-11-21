# Glam by Lynn E2E Tests

This directory contains end-to-end tests for the Glam by Lynn web application using [Playwright](https://playwright.dev/).

## Directory Structure

```
e2e/
├── fixtures/           # Test fixtures and authentication setup
├── helpers/            # Helper utilities for common test operations
│   ├── navigation.ts   # Navigation helpers
│   ├── cart.ts         # Cart interaction helpers
│   ├── forms.ts        # Form filling helpers
│   └── bookings.ts     # Booking flow helpers
├── user-journeys/      # Complete user journey tests
├── checkout/           # Checkout flow tests
├── bookings/           # Booking flow tests
├── admin/              # Admin operations tests
├── example.spec.ts     # Example test to verify setup
└── README.md           # This file
```

## Running Tests

### Prerequisites

1. Ensure both backend and frontend servers are running:
   ```bash
   # Terminal 1 - Backend
   cd backend
   python3 -m uvicorn app.main:app --reload

   # Terminal 2 - Frontend (for manual testing)
   cd frontend
   npm run dev
   ```

2. For CI/CD, the Playwright config will automatically start the dev server.

### Test Commands

```bash
# Run all tests (headless mode)
npm run test:e2e

# Run tests with UI mode (recommended for development)
npm run test:e2e:ui

# Run tests in headed mode (see browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Show test report (after tests have run)
npm run test:e2e:report
```

### Running Specific Tests

```bash
# Run a specific test file
npx playwright test e2e/example.spec.ts

# Run tests matching a pattern
npx playwright test e2e/user-journeys

# Run a specific test by name
npx playwright test -g "should load and display main navigation"
```

### Browser Selection

```bash
# Run tests in specific browser
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# Run tests in all browsers
npx playwright test --project=chromium --project=firefox --project=webkit
```

## Test Categories

### User Journeys (`user-journeys/`)
Complete end-to-end flows that simulate real user interactions:
- Visitor to purchase journey
- Service booking journey
- Authenticated user reorder journey
- Wishlist journey

### Checkout Flows (`checkout/`)
Tests for e-commerce checkout processes:
- Guest checkout
- Authenticated checkout
- Promo code application
- Multiple items checkout
- Validation tests
- Cart persistence

### Booking Flows (`bookings/`)
Tests for service booking system:
- New booking creation
- Booking as authenticated/guest user
- Booking management (view, filter, cancel)
- Calendar restrictions

### Admin Operations (`admin/`)
Tests for administrative functionality:
- Product management
- Booking management
- Calendar management
- Access control

## Writing Tests

### Using Helpers

The test helpers provide reusable functions for common operations:

```typescript
import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';
import { CartHelpers } from '../helpers/cart';

test('add product to cart', async ({ page }) => {
  const nav = new NavigationHelpers(page);
  const cart = new CartHelpers(page);

  await nav.goToProducts();
  await cart.addFirstProductToCart();
  await cart.verifyCartCount(1);
});
```

### Authentication

Use authentication fixtures for testing protected routes:

```typescript
import { test, expect } from '../fixtures/auth.fixture';

test('view my bookings', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/bookings');
  // Test as authenticated user
});

test('admin operations', async ({ adminPage }) => {
  await adminPage.goto('/admin/bookings');
  // Test as admin
});
```

## Best Practices

1. **Use Page Object Models**: Create reusable page objects for complex pages
2. **Use Helpers**: Leverage the helper utilities instead of duplicating code
3. **Clear Test Names**: Use descriptive test names that explain what is being tested
4. **Test Isolation**: Each test should be independent and not rely on others
5. **Wait for Stability**: Use `waitForLoadState('networkidle')` instead of arbitrary timeouts
6. **Flexible Selectors**: Use multiple selector strategies with `.or()` for resilience
7. **Verify State**: Always assert expected outcomes, don't just perform actions

## Configuration

The Playwright configuration is in `playwright.config.ts` at the frontend root. Key settings:

- **Base URL**: `http://localhost:3000` (configurable via `BASE_URL` env var)
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Retries**: 2 retries on CI, 0 locally
- **Video**: Recorded on retry
- **Screenshots**: Captured on failure
- **Trace**: Captured on first retry

## Continuous Integration

Tests are configured to run in CI with:
- Automatic dev server startup
- GitHub Actions reporter
- Parallel execution (1 worker in CI)
- Retry on failure (2 attempts)

## Troubleshooting

### Tests Failing to Start

If tests fail to start the dev server:
```bash
# Check that ports are available
lsof -i :3000
lsof -i :8000

# Kill conflicting processes if needed
kill -9 <PID>
```

### Browser Dependencies

If you encounter browser dependency issues:
```bash
# Install system dependencies (Linux)
sudo npx playwright install-deps

# Or install browsers manually
npx playwright install
```

### Debugging Failed Tests

1. Use UI mode for interactive debugging:
   ```bash
   npm run test:e2e:ui
   ```

2. Use debug mode to step through tests:
   ```bash
   npm run test:e2e:debug
   ```

3. Check test artifacts:
   - Screenshots: `test-results/` directory
   - Videos: `test-results/` directory
   - Traces: `test-results/` directory (view with `npx playwright show-trace`)

## Resources

- [Playwright Documentation](https://playwright.dev/docs/intro)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Playwright API Reference](https://playwright.dev/docs/api/class-playwright)
- [Project Testing Guide](../TESTING.md)
