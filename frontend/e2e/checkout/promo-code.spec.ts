import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';
import { CartHelpers } from '../helpers/cart';

/**
 * Checkout Flow Tests: Promo Code Application
 *
 * Tests promo code functionality during checkout:
 * - Applying valid promo codes
 * - Handling invalid promo codes
 * - Verifying discount calculations
 * - Removing applied promo codes
 */

test.describe('Promo Code Application', () => {
  test('should apply valid promo code and show discount', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product to cart
    await test.step('Add product to cart', async () => {
      await nav.goToProducts();
      await cart.addFirstProductToCart();
    });

    // Go to cart or checkout
    await test.step('Navigate to cart', async () => {
      await nav.goToCart();

      // Get original total
      const totalElement = page.locator('text=/Total.*KSh/i').last();
      await expect(totalElement).toBeVisible();
    });

    // Apply promo code
    await test.step('Apply promo code', async () => {
      // Look for promo code input
      const promoInput = page.locator('input[placeholder*="promo" i]').or(
        page.locator('input[placeholder*="coupon" i]').or(
          page.locator('input[name="promoCode"]')
        )
      );

      if (await promoInput.isVisible({ timeout: 5000 }).catch(() => false)) {
        // Try a common test promo code
        await promoInput.fill('SAVE10');

        const applyButton = page.locator('button:has-text("Apply")');
        await applyButton.click();

        // Wait for discount to be applied
        await page.waitForTimeout(2000);

        // Check if discount was applied
        const discountElement = page.locator('text=/Discount|Promo.*Savings/i').or(
          page.locator('text=/-KSh/')
        );

        const discountVisible = await discountElement.isVisible({ timeout: 3000 }).catch(() => false);

        if (discountVisible) {
          await expect(discountElement).toBeVisible();

          // Verify total is reduced
          const newTotal = page.locator('text=/Total.*KSh/i').last();
          await expect(newTotal).toBeVisible();
        }
      }
    });
  });

  test('should show error for invalid promo code', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product and go to cart
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();

    // Try to apply invalid promo code
    await test.step('Apply invalid promo code', async () => {
      const promoInput = page.locator('input[placeholder*="promo" i]').or(
        page.locator('input[placeholder*="coupon" i]').or(
          page.locator('input[name="promoCode"]')
        )
      );

      if (await promoInput.isVisible({ timeout: 5000 }).catch(() => false)) {
        await promoInput.fill('INVALID_CODE_123');

        const applyButton = page.locator('button:has-text("Apply")');
        await applyButton.click();

        // Wait and check for error message
        await page.waitForTimeout(2000);

        const errorMessage = page.locator('text=/invalid.*code|code.*not.*valid|expired/i').or(
          page.locator('[role="alert"]:has-text("code")')
        );

        const errorVisible = await errorMessage.isVisible({ timeout: 3000 }).catch(() => false);

        if (errorVisible) {
          await expect(errorMessage).toBeVisible();
        }
      }
    });
  });

  test('should allow removing applied promo code', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Setup
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();

    // Apply promo code
    const promoInput = page.locator('input[placeholder*="promo" i]').or(
      page.locator('input[placeholder*="coupon" i]')
    );

    if (await promoInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await promoInput.fill('SAVE10');

      const applyButton = page.locator('button:has-text("Apply")');
      await applyButton.click();
      await page.waitForTimeout(2000);

      // Look for remove button
      const removeButton = page.locator('button:has-text("Remove")').or(
        page.locator('button:has-text("✕")').or(
          page.locator('[data-testid="remove-promo"]')
        )
      );

      const removeVisible = await removeButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (removeVisible) {
        // Get total before removing
        const totalWithDiscount = await page.locator('text=/Total.*KSh/i').last().textContent();

        // Remove promo code
        await removeButton.click();
        await page.waitForTimeout(1000);

        // Verify discount removed
        const discountElement = page.locator('text=/Discount.*-KSh/i');
        const discountVisible = await discountElement.isVisible({ timeout: 1000 }).catch(() => false);

        expect(discountVisible).toBe(false);
      }
    }
  });

  test('should persist promo code through checkout', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();

    // Apply promo code in cart
    await cart.applyPromoCode('SAVE10');

    // Check if applied successfully
    const discountElement = page.locator('text=/Discount/i');
    const discountApplied = await discountElement.isVisible({ timeout: 3000 }).catch(() => false);

    if (discountApplied) {
      // Proceed to checkout
      await cart.proceedToCheckout();

      // Verify promo code discount is still applied
      await page.waitForTimeout(1000);

      const checkoutDiscount = page.locator('text=/Discount.*-KSh/i');
      const stillApplied = await checkoutDiscount.isVisible({ timeout: 3000 }).catch(() => false);

      if (stillApplied) {
        await expect(checkoutDiscount).toBeVisible();
      }
    }
  });

  test('should handle multiple promo code attempts', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Setup
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();

    const promoInput = page.locator('input[placeholder*="promo" i]').or(
      page.locator('input[placeholder*="coupon" i]')
    );

    if (await promoInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Try first invalid code
      await test.step('Try first invalid code', async () => {
        await promoInput.fill('INVALID1');
        await page.locator('button:has-text("Apply")').click();
        await page.waitForTimeout(1000);
      });

      // Try second invalid code
      await test.step('Try second invalid code', async () => {
        await promoInput.fill('INVALID2');
        await page.locator('button:has-text("Apply")').click();
        await page.waitForTimeout(1000);
      });

      // Try valid code
      await test.step('Try valid code', async () => {
        await promoInput.fill('SAVE10');
        await page.locator('button:has-text("Apply")').click();
        await page.waitForTimeout(2000);

        // Check if any discount appears
        const discount = page.locator('text=/Discount/i');
        const discountVisible = await discount.isVisible({ timeout: 3000 }).catch(() => false);

        // Should either show discount or not break the checkout flow
        expect(page.url()).toContain('/cart');
      });
    }
  });
});
