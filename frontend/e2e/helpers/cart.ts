import { Page, expect } from '@playwright/test';

/**
 * Cart interaction helpers
 */

export class CartHelpers {
  constructor(private page: Page) {}

  /**
   * Add a product to cart by clicking the first "Add to Cart" button
   */
  async addFirstProductToCart() {
    const addToCartButton = this.page.locator('button:has-text("Add to Cart")').first();
    await addToCartButton.click();

    // Wait for cart to update (adjust selector based on actual implementation)
    await this.page.waitForTimeout(1000);
  }

  /**
   * Add a specific product to cart by product ID
   */
  async addProductToCartById(productId: string) {
    await this.page.goto(`/products/${productId}`);
    await this.page.waitForLoadState('networkidle');

    const addToCartButton = this.page.locator('button:has-text("Add to Cart")');
    await addToCartButton.click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * Update product quantity in cart
   */
  async updateQuantity(productIndex: number, quantity: number) {
    const quantityInput = this.page.locator('input[type="number"]').nth(productIndex);
    await quantityInput.fill(quantity.toString());
    await quantityInput.press('Enter');
    await this.page.waitForTimeout(500);
  }

  /**
   * Remove item from cart
   */
  async removeItem(productIndex: number) {
    const removeButton = this.page.locator('button:has-text("Remove")').nth(productIndex);
    await removeButton.click();
    await this.page.waitForTimeout(500);
  }

  /**
   * Verify cart item count
   */
  async verifyCartCount(expectedCount: number) {
    const cartBadge = this.page.locator('[data-testid="cart-count"]').or(
      this.page.locator('.cart-count')
    );

    if (expectedCount > 0) {
      await expect(cartBadge).toHaveText(expectedCount.toString());
    }
  }

  /**
   * Verify cart total
   */
  async verifyCartTotal(expectedTotal: string) {
    const totalElement = this.page.locator('[data-testid="cart-total"]').or(
      this.page.locator('text=/Total.*KSh/)').last()
    );
    await expect(totalElement).toContainText(expectedTotal);
  }

  /**
   * Proceed to checkout
   */
  async proceedToCheckout() {
    const checkoutButton = this.page.locator('button:has-text("Checkout")').or(
      this.page.locator('a:has-text("Proceed to Checkout")')
    );
    await checkoutButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Apply promo code
   */
  async applyPromoCode(code: string) {
    const promoInput = this.page.locator('input[placeholder*="promo" i], input[placeholder*="coupon" i]');
    await promoInput.fill(code);

    const applyButton = this.page.locator('button:has-text("Apply")');
    await applyButton.click();
    await this.page.waitForTimeout(1000);
  }

  /**
   * Verify promo code success
   */
  async verifyPromoCodeApplied(discountAmount: string) {
    const discountElement = this.page.locator('text=/Discount.*-KSh/');
    await expect(discountElement).toContainText(discountAmount);
  }
}
