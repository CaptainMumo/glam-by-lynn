import { test as base, expect, Page } from '@playwright/test';

/**
 * Authentication fixtures for testing protected routes
 * Provides authenticated page contexts for testing admin and user flows
 */

type AuthFixtures = {
  authenticatedPage: Page;
  adminPage: Page;
};

/**
 * Helper to set up authentication state
 * In a real scenario, you would:
 * 1. Use API calls to create a session
 * 2. Set cookies/localStorage
 * 3. Or use Playwright's storage state feature
 */
async function setupAuth(page: Page, isAdmin = false) {
  // Navigate to sign-in page
  await page.goto('/auth/signin');

  // TODO: Implement actual Google OAuth flow or mock authentication
  // For now, this is a placeholder
  // In production, you would:
  // - Mock the OAuth callback
  // - Set the session cookie/token
  // - Or use storageState to save and reuse authentication

  // Example: Set mock session (adjust based on actual implementation)
  await page.evaluate((adminStatus) => {
    // Mock session data in localStorage or cookies
    localStorage.setItem('mock-session', JSON.stringify({
      user: {
        email: adminStatus ? 'admin@glamby lynn.com' : 'user@example.com',
        name: adminStatus ? 'Admin User' : 'Test User',
        isAdmin: adminStatus,
        adminRole: adminStatus ? 'super_admin' : null,
      }
    }));
  }, isAdmin);
}

/**
 * Extended test with authentication fixtures
 */
export const test = base.extend<AuthFixtures>({
  /**
   * Authenticated page fixture for regular users
   */
  authenticatedPage: async ({ page }, use) => {
    await setupAuth(page, false);
    await use(page);
  },

  /**
   * Authenticated page fixture for admin users
   */
  adminPage: async ({ page }, use) => {
    await setupAuth(page, true);
    await use(page);
  },
});

export { expect };
