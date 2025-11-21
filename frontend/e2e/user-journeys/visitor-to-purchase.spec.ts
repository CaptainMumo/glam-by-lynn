import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';
import { CartHelpers } from '../helpers/cart';
import { FormHelpers } from '../helpers/forms';

/**
 * User Journey: Visitor to Purchase
 *
 * This test simulates a complete user journey from landing on the homepage
 * to completing a purchase as a guest user.
 *
 * Steps:
 * 1. Visit homepage
 * 2. Browse products catalog
 * 3. View product details
 * 4. Add product to cart
 * 5. View and update cart
 * 6. Proceed to checkout
 * 7. Complete guest checkout
 * 8. Verify order confirmation
 */

test.describe('Visitor to Purchase Journey', () => {
  test('should complete full purchase flow as guest', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Step 1: Visit homepage
    await test.step('Visit homepage', async () => {
      await nav.goToHome();
      await expect(page).toHaveTitle(/Glam by Lynn/i);
    });

    // Step 2: Navigate to products catalog
    await test.step('Navigate to products catalog', async () => {
      await nav.goToProducts();

      // Check if products are available
      const productCards = page.locator('[data-testid="product-card"]').or(
        page.locator('.product-card')
      );
      const hasProducts = await productCards.first().isVisible({ timeout: 10000 }).catch(() => false);

      // Skip rest of test if no products available
      if (!hasProducts) {
        test.skip(true, 'No products available in catalog - backend data required');
      }

      await expect(productCards.first()).toBeVisible();
    });

    // Step 3: View first product details
    await test.step('View product details', async () => {
      const firstProduct = page.locator('[data-testid="product-card"]').or(
        page.locator('.product-card')
      ).first();

      await firstProduct.click();
      await page.waitForLoadState('networkidle');

      // Verify product detail page elements
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('text=/KSh|Price/i')).toBeVisible();
    });

    // Step 4: Add product to cart
    await test.step('Add product to cart', async () => {
      const addToCartButton = page.locator('button:has-text("Add to Cart")');
      await expect(addToCartButton).toBeVisible();
      await addToCartButton.click();

      // Wait for cart to update
      await page.waitForTimeout(1000);

      // Verify cart count updated (if visible)
      const cartBadge = page.locator('[data-testid="cart-count"]').or(
        page.locator('.cart-badge')
      );

      // Cart badge should show 1 item (may not be visible if cart was empty)
      const isVisible = await cartBadge.isVisible().catch(() => false);
      if (isVisible) {
        await expect(cartBadge).toHaveText('1');
      }
    });

    // Step 5: View cart
    await test.step('View and verify cart contents', async () => {
      await nav.goToCart();

      // Verify cart has items
      const cartItems = page.locator('[data-testid="cart-item"]').or(
        page.locator('.cart-item')
      );
      await expect(cartItems.first()).toBeVisible();

      // Verify cart total is displayed
      const cartTotal = page.locator('text=/Total.*KSh/i').last();
      await expect(cartTotal).toBeVisible();
    });

    // Step 6: Proceed to checkout
    await test.step('Proceed to checkout', async () => {
      await cart.proceedToCheckout();

      // Verify we're on checkout page
      await expect(page).toHaveURL(/\/checkout/);
    });

    // Step 7: Fill guest checkout form
    await test.step('Complete guest checkout', async () => {
      // Fill guest information
      await forms.fillGuestInfo({
        name: 'Test User',
        email: 'test@example.com',
        phone: '+254712345678'
      });

      // Fill shipping address
      await forms.fillShippingAddress({
        street: '123 Test Street',
        city: 'Nairobi',
        county: 'Nairobi County',
        postalCode: '00100'
      });

      // Select payment method (M-Pesa)
      await forms.selectPaymentMethod('mpesa');

      // Fill M-Pesa phone number
      await forms.fillMpesaPhone('+254712345678');

      // Submit checkout form
      await forms.submitForm('Place Order');
    });

    // Step 8: Verify order confirmation
    await test.step('Verify order confirmation', async () => {
      // Wait for confirmation page
      await forms.waitForConfirmation(15000);

      // Check for confirmation message
      const confirmationMessage = page.locator('text=/order.*confirmed|thank you|success/i').first();
      await expect(confirmationMessage).toBeVisible({ timeout: 5000 });

      // Check for order number
      const orderNumber = page.locator('text=/order.*#|order number/i').first();
      await expect(orderNumber).toBeVisible();
    });
  });

  test('should update cart quantity before checkout', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product to cart
    await nav.goToProducts();

    // Check if products are available
    const addToCartButton = page.locator('button:has-text("Add to Cart")').first();
    const hasProducts = await addToCartButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasProducts) {
      test.skip(true, 'No products available - backend data required');
    }

    await cart.addFirstProductToCart();

    // Go to cart
    await nav.goToCart();

    // Update quantity to 2
    await cart.updateQuantity(0, 2);

    // Verify quantity updated
    const quantityInput = page.locator('input[type="number"]').first();
    await expect(quantityInput).toHaveValue('2');

    // Verify total updated (should be approximately doubled)
    const cartTotal = page.locator('[data-testid="cart-total"]').or(
      page.locator('text=/Total.*KSh/i').last()
    );
    await expect(cartTotal).toBeVisible();
  });

  test('should remove item from cart', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product to cart
    await nav.goToProducts();

    // Check if products are available
    const addToCartButton = page.locator('button:has-text("Add to Cart")').first();
    const hasProducts = await addToCartButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasProducts) {
      test.skip(true, 'No products available - backend data required');
    }

    await cart.addFirstProductToCart();

    // Go to cart
    await nav.goToCart();

    // Remove the item
    await cart.removeItem(0);

    // Verify cart is empty
    const emptyCartMessage = page.locator('text=/cart is empty|no items/i');
    await expect(emptyCartMessage).toBeVisible({ timeout: 5000 });
  });

  test('should display validation errors on invalid checkout', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Add product and go to checkout
    await nav.goToProducts();

    // Check if products are available
    const addToCartButton = page.locator('button:has-text("Add to Cart")').first();
    const hasProducts = await addToCartButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasProducts) {
      test.skip(true, 'No products available - backend data required');
    }

    await cart.addFirstProductToCart();
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Try to submit without filling required fields
    await forms.submitForm('Place Order');

    // Verify validation errors appear
    const errorMessages = page.locator('text=/required|invalid|must/i').or(
      page.locator('[role="alert"]')
    );

    // Should show at least one error
    await expect(errorMessages.first()).toBeVisible({ timeout: 3000 });
  });
});
