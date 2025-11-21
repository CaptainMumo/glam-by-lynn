import { Page, expect } from '@playwright/test';

/**
 * Booking flow helpers
 */

export interface BookingDetails {
  packageName?: string;
  date: string; // YYYY-MM-DD format
  timeSlot: string; // HH:MM format
  location: 'Nairobi' | 'Kitui';
  numBrides?: number;
  numMaids?: number;
  numMothers?: number;
  numOthers?: number;
  weddingTheme?: string;
  specialRequests?: string;
}

export class BookingHelpers {
  constructor(private page: Page) {}

  /**
   * Select a service package
   */
  async selectPackage(packageName: string) {
    // Navigate to services if not already there
    const currentUrl = this.page.url();
    if (!currentUrl.includes('/services')) {
      await this.page.goto('/services');
      await this.page.waitForLoadState('networkidle');
    }

    // Click on the package card or "Book Now" button
    const packageCard = this.page.locator(`text=${packageName}`).first();
    await packageCard.scrollIntoViewIfNeeded();

    const bookButton = packageCard.locator('..').locator('button:has-text("Book")').or(
      packageCard.locator('..').locator('a:has-text("Book")')
    );
    await bookButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Fill booking details
   */
  async fillBookingDetails(details: BookingDetails) {
    // Select date
    const dateInput = this.page.locator('input[type="date"]');
    await dateInput.fill(details.date);

    // Select time slot (using shadcn/ui combobox)
    const timeCombobox = this.page.getByRole('combobox', { name: 'Time *' }).or(
      this.page.locator('button:has-text("Select time")')
    );
    await timeCombobox.click();
    await this.page.locator(`[role="option"]:has-text("${details.timeSlot}")`).first().click();

    // Select location (using shadcn/ui combobox)
    const locationCombobox = this.page.getByRole('combobox', { name: 'Location *' }).or(
      this.page.locator('button:has-text("Select location")')
    );
    await locationCombobox.click();
    await this.page.locator(`[role="option"]:has-text("${details.location}")`).first().click();

    // Fill participant numbers
    if (details.numBrides !== undefined) {
      await this.page.fill('input[name="numBrides"], input[placeholder*="Bride" i]', details.numBrides.toString());
    }

    if (details.numMaids !== undefined) {
      await this.page.fill('input[name="numMaids"], input[placeholder*="Maid" i]', details.numMaids.toString());
    }

    if (details.numMothers !== undefined) {
      await this.page.fill('input[name="numMothers"], input[placeholder*="Mother" i]', details.numMothers.toString());
    }

    if (details.numOthers !== undefined) {
      await this.page.fill('input[name="numOthers"], input[placeholder*="Other" i]', details.numOthers.toString());
    }

    // Fill optional fields
    if (details.weddingTheme) {
      await this.page.fill('input[name="weddingTheme"], input[placeholder*="theme" i]', details.weddingTheme);
    }

    if (details.specialRequests) {
      await this.page.fill('textarea[name="specialRequests"], textarea[placeholder*="special" i]', details.specialRequests);
    }
  }

  /**
   * Submit booking
   */
  async submitBooking() {
    const submitButton = this.page.locator('button:has-text("Confirm Booking")').or(
      this.page.locator('button:has-text("Book Now")')
    ).or(
      this.page.locator('button[type="submit"]')
    );
    await submitButton.click();
  }

  /**
   * Verify booking confirmation
   */
  async verifyBookingConfirmation() {
    // Wait for confirmation page
    await this.page.waitForURL(/\/bookings\/.*\/confirmation/, { timeout: 10000 });

    // Check for confirmation message
    const confirmationText = this.page.locator('text=/Booking Confirmed|Successfully Booked/i');
    await expect(confirmationText).toBeVisible();

    // Check for booking number
    const bookingNumber = this.page.locator('text=/Booking.*#[A-Z0-9]+/i');
    await expect(bookingNumber).toBeVisible();
  }

  /**
   * View booking details in My Bookings
   */
  async viewBookingInHistory(bookingNumber: string) {
    await this.page.goto('/bookings');
    await this.page.waitForLoadState('networkidle');

    const bookingLink = this.page.locator(`text=${bookingNumber}`);
    await expect(bookingLink).toBeVisible();
    await bookingLink.click();
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Cancel a booking
   */
  async cancelBooking(bookingNumber: string) {
    await this.viewBookingInHistory(bookingNumber);

    // Click cancel button
    const cancelButton = this.page.locator('button:has-text("Cancel")');
    await cancelButton.click();

    // Confirm cancellation in dialog
    this.page.on('dialog', dialog => dialog.accept());
    await this.page.waitForTimeout(1000);

    // Verify cancellation
    const cancelledStatus = this.page.locator('text=/Cancelled/i');
    await expect(cancelledStatus).toBeVisible();
  }

  /**
   * Filter bookings by status
   */
  async filterBookingsByStatus(status: string) {
    const statusFilter = this.page.locator('select').filter({ hasText: /status/i }).or(
      this.page.locator('select:has(option:has-text("status"))')
    );
    await statusFilter.selectOption(status);
    await this.page.waitForTimeout(1000);
  }
}
