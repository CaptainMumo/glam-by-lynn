import { Page } from '@playwright/test';

/**
 * Navigation helpers for common user flows
 */

export class NavigationHelpers {
  constructor(private page: Page) {}

  /**
   * Navigate to homepage
   */
  async goToHome() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to products page
   */
  async goToProducts() {
    await this.page.goto('/products');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to services page
   */
  async goToServices() {
    await this.page.goto('/services');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to cart
   */
  async goToCart() {
    await this.page.goto('/cart');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to checkout
   */
  async goToCheckout() {
    await this.page.goto('/checkout');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to booking page
   */
  async goToNewBooking() {
    await this.page.goto('/bookings/new');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to my bookings
   */
  async goToMyBookings() {
    await this.page.goto('/bookings');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to admin dashboard
   */
  async goToAdminDashboard() {
    await this.page.goto('/admin');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to admin bookings
   */
  async goToAdminBookings() {
    await this.page.goto('/admin/bookings');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to admin calendar
   */
  async goToAdminCalendar() {
    await this.page.goto('/admin/calendar');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Navigate to admin products
   */
  async goToAdminProducts() {
    await this.page.goto('/admin/products');
    await this.page.waitForLoadState('networkidle');
  }
}
