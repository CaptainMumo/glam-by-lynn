import { test, expect } from '@playwright/test';

/**
 * Example test to verify Playwright setup
 * This test can be run to verify the testing infrastructure is working
 */

test.describe('Homepage', () => {
  test('should load and display main navigation', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for page to load
    await page.waitForLoadState('networkidle');

    // Check that the page title is correct
    await expect(page).toHaveTitle(/Glam by Lynn/i);

    // Check that main navigation elements are visible
    const header = page.locator('header');
    await expect(header).toBeVisible();

    // Check for key navigation links (use first() to avoid strict mode violations)
    const productsLink = page.locator('a:has-text("Products")').first();
    const servicesLink = page.locator('a:has-text("Services")').first();

    await expect(productsLink).toBeVisible();
    await expect(servicesLink).toBeVisible();
  });

  test('should display brand name or logo', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Look for brand name in header or any heading containing "Glam"
    const brandElement = page.locator('header').locator('text=/Glam/i').first().or(
      page.locator('h1, h2, h3').locator('text=/Glam/i').first()
    );

    // Should find at least one element with "Glam" in the page
    await expect(brandElement).toBeVisible({ timeout: 10000 });
  });

  test('should have functional cart icon', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Look for cart icon or link
    const cartIcon = page.locator('a[href*="/cart"]').or(
      page.locator('[data-testid="cart-icon"]')
    );

    // Cart should be visible
    await expect(cartIcon).toBeVisible({ timeout: 5000 });
  });
});
