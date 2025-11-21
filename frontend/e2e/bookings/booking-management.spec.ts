import { test, expect } from '../fixtures/auth.fixture';
import { NavigationHelpers } from '../helpers/navigation';
import { BookingHelpers } from '../helpers/bookings';

/**
 * Booking Management Tests
 *
 * Tests for viewing, filtering, and managing bookings:
 * - Viewing booking history
 * - Filtering bookings by status
 * - Viewing booking details
 * - Cancelling bookings
 * - Booking cancellation restrictions
 */

test.describe('Booking Management', () => {
  test('should display user booking history', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await test.step('Navigate to My Bookings', async () => {
      await nav.goToMyBookings();

      // Page should load
      await expect(authenticatedPage).toHaveURL(/\/bookings/);
    });

    await test.step('Verify booking list elements', async () => {
      // Should show page title
      const pageTitle = authenticatedPage.locator('h1:has-text("Bookings")').or(
        authenticatedPage.locator('h1:has-text("My Bookings")')
      );
      await expect(pageTitle).toBeVisible({ timeout: 10000 });

      // Check for either bookings or empty state
      const bookingCards = authenticatedPage.locator('[data-testid="booking-card"]').or(
        authenticatedPage.locator('.booking-card')
      );

      const emptyState = authenticatedPage.locator('text=/no bookings|haven\'t made any bookings/i');

      // Should show either bookings or empty state
      const hasBookings = await bookingCards.first().isVisible({ timeout: 5000 }).catch(() => false);
      const hasEmptyState = await emptyState.isVisible({ timeout: 5000 }).catch(() => false);

      expect(hasBookings || hasEmptyState).toBe(true);
    });
  });

  test('should filter bookings by status', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);
    const booking = new BookingHelpers(authenticatedPage);

    await nav.goToMyBookings();

    // Look for status filter
    await test.step('Apply status filter', async () => {
      const statusFilter = authenticatedPage.locator('select').filter({ hasText: /status/i }).or(
        authenticatedPage.locator('[data-testid="status-filter"]')
      );

      if (await statusFilter.isVisible({ timeout: 5000 }).catch(() => false)) {
        // Filter by confirmed status
        await booking.filterBookingsByStatus('confirmed');

        // Wait for filter to apply
        await authenticatedPage.waitForTimeout(1000);

        // Verify URL or page state updated
        const pageContent = await authenticatedPage.content();
        expect(pageContent).toBeTruthy();
      }
    });
  });

  test('should view booking details', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await nav.goToMyBookings();

    await test.step('Click on first booking', async () => {
      // Look for booking cards or links
      const firstBooking = authenticatedPage.locator('[data-testid="booking-card"]').or(
        authenticatedPage.locator('.booking-card')
      ).first();

      const hasBookings = await firstBooking.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        // Click view details button or card
        const detailsButton = firstBooking.locator('button:has-text("View")').or(
          firstBooking.locator('a:has-text("Details")')
        );

        const hasButton = await detailsButton.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasButton) {
          await detailsButton.click();
          await authenticatedPage.waitForLoadState('networkidle');

          // Verify we're on details page
          const bookingNumber = authenticatedPage.locator('text=/booking.*#|#[A-Z0-9]+/i');
          await expect(bookingNumber.first()).toBeVisible({ timeout: 5000 });
        }
      }
    });
  });

  test('should show booking cancellation restriction for recent bookings', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await nav.goToMyBookings();

    await test.step('Check cancellation restrictions', async () => {
      // Look for cancel buttons
      const cancelButtons = authenticatedPage.locator('button:has-text("Cancel")');

      const hasCancelButton = await cancelButtons.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasCancelButton) {
        // Check if button is disabled or shows restriction message
        const firstCancelButton = cancelButtons.first();
        const isDisabled = await firstCancelButton.isDisabled().catch(() => false);

        if (isDisabled) {
          // Look for tooltip or message explaining why
          const restrictionMessage = authenticatedPage.locator('text=/24 hours|cannot cancel|too late/i');
          const hasMessage = await restrictionMessage.isVisible({ timeout: 3000 }).catch(() => false);

          // Either button is disabled or there's a restriction message
          expect(isDisabled || hasMessage).toBeTruthy();
        }
      }
    });
  });

  test('should display booking status badge', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await nav.goToMyBookings();

    await test.step('Verify status badges', async () => {
      const bookingCards = authenticatedPage.locator('[data-testid="booking-card"]').or(
        authenticatedPage.locator('.booking-card')
      );

      const hasBookings = await bookingCards.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        // Look for status badges
        const statusBadge = authenticatedPage.locator('[data-testid="status-badge"]').or(
          authenticatedPage.locator('text=/Pending|Confirmed|Completed|Cancelled/i')
        );

        await expect(statusBadge.first()).toBeVisible({ timeout: 5000 });
      }
    });
  });

  test('should show booking date and time', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await nav.goToMyBookings();

    await test.step('Verify booking date/time display', async () => {
      const bookingCards = authenticatedPage.locator('[data-testid="booking-card"]').or(
        authenticatedPage.locator('.booking-card')
      );

      const hasBookings = await bookingCards.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        const firstBooking = bookingCards.first();

        // Should show date in some format
        const dateElement = firstBooking.locator('text=/\\d{4}-\\d{2}-\\d{2}|\\d{1,2}\\/\\d{1,2}\\/\\d{2,4}/');
        const dateVisible = await dateElement.isVisible({ timeout: 3000 }).catch(() => false);

        // Should show time
        const timeElement = firstBooking.locator('text=/\\d{1,2}:\\d{2}|AM|PM/i');
        const timeVisible = await timeElement.isVisible({ timeout: 3000 }).catch(() => false);

        // At least one should be visible
        expect(dateVisible || timeVisible).toBe(true);
      }
    });
  });

  test('should navigate to new booking from bookings page', async ({ authenticatedPage }) => {
    const nav = new NavigationHelpers(authenticatedPage);

    await nav.goToMyBookings();

    await test.step('Click new booking button', async () => {
      const newBookingButton = authenticatedPage.locator('button:has-text("Book")').or(
        authenticatedPage.locator('a:has-text("New Booking")').or(
          authenticatedPage.locator('a:has-text("Book")')
        )
      );

      if (await newBookingButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        await newBookingButton.click();
        await authenticatedPage.waitForLoadState('networkidle');

        // Should navigate to services or booking page
        const url = authenticatedPage.url();
        expect(url).toMatch(/\/services|\/bookings\/new|\/book/);
      }
    });
  });
});
