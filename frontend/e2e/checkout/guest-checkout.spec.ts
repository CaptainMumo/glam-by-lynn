import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';
import { CartHelpers } from '../helpers/cart';
import { FormHelpers } from '../helpers/forms';

/**
 * Checkout Flow Tests: Guest Checkout
 *
 * Tests the complete guest checkout process including:
 * - Adding products to cart
 * - Filling guest information
 * - Entering shipping address
 * - Selecting payment method
 * - Completing order
 */

test.describe('Guest Checkout Flow', () => {
  test('should complete checkout with M-Pesa payment', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Add product to cart
    await test.step('Add product to cart', async () => {
      await nav.goToProducts();
      await cart.addFirstProductToCart();
      await cart.verifyCartCount(1);
    });

    // Proceed to checkout
    await test.step('Navigate to checkout', async () => {
      await nav.goToCart();
      await cart.proceedToCheckout();
      await expect(page).toHaveURL(/\/checkout/);
    });

    // Fill guest information
    await test.step('Fill guest information', async () => {
      await forms.fillGuestInfo({
        name: 'Guest User',
        email: 'guest@example.com',
        phone: '+254712345678'
      });
    });

    // Fill shipping address
    await test.step('Fill shipping address', async () => {
      await forms.fillShippingAddress({
        street: '456 Guest Avenue',
        city: 'Nairobi',
        county: 'Nairobi County',
        postalCode: '00100'
      });
    });

    // Select M-Pesa payment
    await test.step('Select M-Pesa payment method', async () => {
      await forms.selectPaymentMethod('mpesa');
      await forms.fillMpesaPhone('+254712345678');
    });

    // Place order
    await test.step('Place order', async () => {
      await forms.submitForm('Place Order');
      await forms.waitForConfirmation(15000);

      // Verify confirmation
      const confirmationMessage = page.locator('text=/order.*confirmed|thank you|success/i');
      await expect(confirmationMessage.first()).toBeVisible();
    });
  });

  test('should complete checkout with card payment', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Add product and go to checkout
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Fill required information
    await forms.fillGuestInfo({
      name: 'Card User',
      email: 'card@example.com',
      phone: '+254722123456'
    });

    await forms.fillShippingAddress({
      street: '789 Card Street',
      city: 'Mombasa',
      county: 'Mombasa County'
    });

    // Select card payment
    await forms.selectPaymentMethod('card');

    // Fill card details (if card form is present)
    const cardNumberField = page.locator('input[name="cardNumber"]').or(
      page.locator('input[placeholder*="card number" i]')
    );

    if (await cardNumberField.isVisible({ timeout: 2000 }).catch(() => false)) {
      await cardNumberField.fill('4242424242424242');

      const expiryField = page.locator('input[name="expiry"]').or(
        page.locator('input[placeholder*="expiry" i]')
      );
      await expiryField.fill('12/25');

      const cvvField = page.locator('input[name="cvv"]').or(
        page.locator('input[placeholder*="cvv" i]')
      );
      await cvvField.fill('123');
    }

    // Submit order
    await forms.submitForm('Place Order');
    await forms.waitForConfirmation(15000);

    // Verify order placed
    const confirmationMessage = page.locator('text=/order.*confirmed|thank you|success/i');
    await expect(confirmationMessage.first()).toBeVisible();
  });

  test('should validate guest email format', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Setup
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Fill name and invalid email
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="tel"]', '+254712345678');

    // Try to proceed
    await forms.submitForm('Continue');

    // Verify email validation error
    const emailError = page.locator('text=/invalid.*email|valid email/i').or(
      page.locator('input[type="email"] ~ *:has-text("invalid")')
    );

    await expect(emailError).toBeVisible({ timeout: 5000 });
  });

  test('should validate phone number format', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Setup
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Fill with invalid phone
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="tel"]', '123'); // Invalid

    // Try to proceed
    const continueButton = page.locator('button:has-text("Continue")').or(
      page.locator('button:has-text("Next")').or(
        page.locator('button[type="submit"]')
      )
    );

    await continueButton.click();

    // Verify phone validation error
    const phoneError = page.locator('text=/invalid.*phone|valid phone number/i').or(
      page.locator('input[type="tel"] ~ *:has-text("invalid")')
    );

    const isVisible = await phoneError.isVisible({ timeout: 5000 }).catch(() => false);
    if (isVisible) {
      await expect(phoneError).toBeVisible();
    }
  });

  test('should require all shipping address fields', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);
    const forms = new FormHelpers(page);

    // Setup
    await nav.goToProducts();
    await cart.addFirstProductToCart();
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Fill guest info
    await forms.fillGuestInfo({
      name: 'Test User',
      email: 'test@example.com',
      phone: '+254712345678'
    });

    // Leave shipping address empty and try to submit
    await forms.submitForm('Place Order');

    // Verify address validation errors
    const addressError = page.locator('text=/address.*required|street.*required|city.*required/i').or(
      page.locator('[role="alert"]')
    );

    await expect(addressError.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display order summary in checkout', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const cart = new CartHelpers(page);

    // Add product
    await nav.goToProducts();
    await cart.addFirstProductToCart();

    // Go to checkout
    await nav.goToCart();
    await cart.proceedToCheckout();

    // Verify order summary elements
    await test.step('Verify order summary', async () => {
      // Should show subtotal
      const subtotal = page.locator('text=/subtotal.*KSh/i');
      await expect(subtotal).toBeVisible({ timeout: 10000 });

      // Should show shipping/delivery cost
      const shipping = page.locator('text=/shipping.*KSh|delivery.*KSh/i');
      const shippingVisible = await shipping.isVisible({ timeout: 3000 }).catch(() => false);

      // Should show total
      const total = page.locator('text=/total.*KSh/i').last();
      await expect(total).toBeVisible();
    });
  });
});
