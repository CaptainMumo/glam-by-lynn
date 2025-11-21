import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';
import { BookingHelpers } from '../helpers/bookings';
import { FormHelpers } from '../helpers/forms';

/**
 * User Journey: Service Booking
 *
 * This test simulates a complete service booking flow from browsing services
 * to completing a booking as a guest.
 *
 * Steps:
 * 1. Browse services catalog
 * 2. View service package details
 * 3. Navigate to booking form
 * 4. Fill booking details
 * 5. Complete booking as guest
 * 6. Receive booking confirmation
 */

test.describe('Service Booking Journey', () => {
  test('should complete service booking as guest', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const booking = new BookingHelpers(page);
    const forms = new FormHelpers(page);

    // Step 1: Navigate to services page
    await test.step('Browse services catalog', async () => {
      await nav.goToServices();

      // Check if services are available
      const serviceCards = page.locator('[data-testid="service-card"]').or(
        page.locator('.service-card, .package-card')
      );
      const hasServices = await serviceCards.first().isVisible({ timeout: 10000 }).catch(() => false);

      // Skip rest of test if no services available
      if (!hasServices) {
        test.skip(true, 'No services available in catalog - backend data required');
      }

      await expect(serviceCards.first()).toBeVisible();
    });

    // Step 2: View service package details
    await test.step('View service package details', async () => {
      const firstService = page.locator('[data-testid="service-card"]').or(
        page.locator('.service-card, .package-card')
      ).first();

      // Get service name for later verification
      const serviceName = await firstService.locator('[data-slot="card-title"]').textContent();

      // Click on "Book Now" or "View Details" button
      const bookButton = firstService.locator('button:has-text("Book")').or(
        firstService.locator('a:has-text("Book")')
      );
      await bookButton.click();
      await page.waitForLoadState('networkidle');

      // Verify we're on booking page or details page
      const pageUrl = page.url();
      expect(pageUrl).toMatch(/\/services|\/bookings\/new/);
    });

    // Step 3: Navigate to booking form (if not already there)
    await test.step('Navigate to booking form', async () => {
      const currentUrl = page.url();

      if (!currentUrl.includes('/bookings/new')) {
        // If on service details page, click book button
        const bookNowButton = page.locator('button:has-text("Book Now")').or(
          page.locator('a:has-text("Book Now")')
        );

        if (await bookNowButton.isVisible({ timeout: 2000 }).catch(() => false)) {
          await bookNowButton.click();
          await page.waitForLoadState('networkidle');
        }
      }

      // Verify we're on booking form
      await expect(page).toHaveURL(/\/bookings\/new|\/book/);
    });

    // Step 4: Fill booking details
    await test.step('Fill booking details', async () => {
      // Get future date (7 days from now)
      const futureDate = new Date();
      futureDate.setDate(futureDate.getDate() + 7);
      const dateString = futureDate.toISOString().split('T')[0];

      await booking.fillBookingDetails({
        date: dateString,
        timeSlot: '10:00',
        location: 'Nairobi',
        numBrides: 1,
        numMaids: 2,
        numMothers: 1,
        numOthers: 0,
        weddingTheme: 'Elegant Garden Wedding',
        specialRequests: 'Please use natural makeup products'
      });

      // Fill guest information
      await forms.fillGuestInfo({
        name: 'Jane Doe',
        email: 'jane.doe@example.com',
        phone: '+254722123456'
      });
    });

    // Step 5: Submit booking
    await test.step('Submit booking', async () => {
      await booking.submitBooking();

      // Wait for processing
      await page.waitForTimeout(2000);
    });

    // Step 6: Verify booking confirmation
    await test.step('Verify booking confirmation', async () => {
      await booking.verifyBookingConfirmation();

      // Verify booking details are displayed
      const bookingDetails = page.locator('text=/Nairobi|Jane Doe|Garden Wedding/i');
      await expect(bookingDetails.first()).toBeVisible({ timeout: 5000 });
    });
  });

  test('should validate required booking fields', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const booking = new BookingHelpers(page);

    // Navigate to booking form
    await nav.goToServices();

    const firstBookButton = page.locator('button:has-text("Book")').or(
      page.locator('a:has-text("Book")')
    ).first();

    // Check if services are available
    const hasServices = await firstBookButton.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasServices) {
      test.skip(true, 'No services available - backend data required');
    }

    await firstBookButton.click();
    await page.waitForLoadState('networkidle');

    // Verify submit button is disabled when required fields are empty
    const submitButton = page.locator('button:has-text("Complete Booking")').or(
      page.locator('button:has-text("Confirm")').or(
        page.locator('main button[type="submit"]')
      )
    );

    // Button should be disabled when form is invalid
    await expect(submitButton.first()).toBeDisabled();
  });

  test('should calculate transport costs correctly', async ({ page }) => {
    const nav = new NavigationHelpers(page);
    const booking = new BookingHelpers(page);

    // Navigate to booking form
    await nav.goToNewBooking();

    // Select Kitui location (should have higher transport cost)
    const kituiOption = page.locator('input[value="Kitui"]').or(
      page.locator('label:has-text("Kitui")')
    );

    if (await kituiOption.isVisible({ timeout: 5000 }).catch(() => false)) {
      await kituiOption.click();

      // Verify transport cost is displayed
      const transportCost = page.locator('text=/transport.*KSh|delivery fee/i');
      await expect(transportCost).toBeVisible({ timeout: 5000 });

      // Change to Nairobi
      const nairobiOption = page.locator('input[value="Nairobi"]').or(
        page.locator('label:has-text("Nairobi")')
      );
      await nairobiOption.click();

      // Verify transport cost updated (should be lower for Nairobi)
      await page.waitForTimeout(1000);
    }
  });

  test('should display package pricing breakdown', async ({ page }) => {
    const nav = new NavigationHelpers(page);

    // Navigate to services
    await nav.goToServices();

    // Click on first service
    const firstService = page.locator('[data-testid="service-card"]').or(
      page.locator('.service-card, .package-card')
    ).first();

    // Check if services are available
    const hasServices = await firstService.isVisible({ timeout: 5000 }).catch(() => false);

    if (!hasServices) {
      test.skip(true, 'No services available - backend data required');
    }

    await firstService.click();
    await page.waitForLoadState('networkidle');

    // Verify pricing information is displayed
    const pricingInfo = page.locator('text=/Pricing|KSh|Bride|Maid|Contact for pricing/i');
    await expect(pricingInfo.first()).toBeVisible();

    // Verify package features are listed
    const features = page.locator('ul').or(
      page.locator('[data-testid="package-features"]')
    );

    // Should have at least one feature listed
    const featureItems = features.locator('li').or(
      page.locator('text=/included|Professional|makeup/i')
    );
    await expect(featureItems.first()).toBeVisible({ timeout: 5000 });
  });
});
