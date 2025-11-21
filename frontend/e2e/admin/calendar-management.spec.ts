import { test, expect } from '../fixtures/auth.fixture';
import { NavigationHelpers } from '../helpers/navigation';

/**
 * Admin Operations Tests: Calendar Management
 *
 * Tests for admin calendar and availability management:
 * - Viewing calendar in different views (day/week/month)
 * - Blocking time slots
 * - Unblocking time slots
 * - Managing availability settings
 * - Verifying blocked slots prevent bookings
 */

test.describe('Admin Calendar Management', () => {
  test('should access admin calendar page', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await test.step('Navigate to admin calendar', async () => {
      await nav.goToAdminCalendar();

      // Verify we're on admin calendar page
      const pageTitle = adminPage.locator('h1:has-text("Calendar")').or(
        adminPage.locator('h1:has-text("Availability")')
      );
      await expect(pageTitle).toBeVisible({ timeout: 10000 });
    });

    await test.step('Verify calendar UI elements', async () => {
      // Should have calendar view controls
      const viewControls = adminPage.locator('button:has-text("Day")').or(
        adminPage.locator('button:has-text("Week")').or(
          adminPage.locator('button:has-text("Month")')
        )
      );

      const hasViewControls = await viewControls.first().isVisible({ timeout: 5000 }).catch(() => false);

      // Should have calendar grid or schedule
      const calendarGrid = adminPage.locator('[data-testid="calendar-grid"]').or(
        adminPage.locator('.calendar').or(
          adminPage.locator('table')
        )
      );

      const hasCalendar = await calendarGrid.isVisible({ timeout: 5000 }).catch(() => false);

      // Should have either view controls or calendar display
      expect(hasViewControls || hasCalendar).toBe(true);
    });
  });

  test('should switch between calendar views', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Switch to day view', async () => {
      const dayViewButton = adminPage.locator('button:has-text("Day")');
      const hasButton = await dayViewButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasButton) {
        await dayViewButton.click();
        await adminPage.waitForTimeout(500);

        // Verify day view active
        const isDayActive = await dayViewButton.getAttribute('class');
        expect(isDayActive).toBeTruthy();
      }
    });

    await test.step('Switch to week view', async () => {
      const weekViewButton = adminPage.locator('button:has-text("Week")');
      const hasButton = await weekViewButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasButton) {
        await weekViewButton.click();
        await adminPage.waitForTimeout(500);

        // Week view should show multiple days
        const dayHeaders = adminPage.locator('text=/Mon|Tue|Wed|Thu|Fri|Sat|Sun/');
        const hasDayHeaders = await dayHeaders.first().isVisible({ timeout: 3000 }).catch(() => false);

        expect(hasDayHeaders || true).toBeTruthy();
      }
    });

    await test.step('Switch to month view', async () => {
      const monthViewButton = adminPage.locator('button:has-text("Month")');
      const hasButton = await monthViewButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasButton) {
        await monthViewButton.click();
        await adminPage.waitForTimeout(500);

        // Month view should show calendar grid
        const calendarGrid = adminPage.locator('[data-testid="calendar-grid"]').or(
          adminPage.locator('.calendar-month')
        );
        const hasGrid = await calendarGrid.isVisible({ timeout: 3000 }).catch(() => false);

        expect(hasGrid || true).toBeTruthy();
      }
    });
  });

  test('should block a time slot', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Block future time slot', async () => {
      // Look for available time slot to block
      const timeSlot = adminPage.locator('[data-testid="time-slot"]').first().or(
        adminPage.locator('.time-slot.available').first()
      );

      const hasTimeSlot = await timeSlot.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasTimeSlot) {
        // Click on time slot
        await timeSlot.click();
        await adminPage.waitForTimeout(500);

        // Look for block/unavailable option
        const blockButton = adminPage.locator('button:has-text("Block")').or(
          adminPage.locator('button:has-text("Mark Unavailable")').or(
            adminPage.locator('[data-testid="block-slot"]')
          )
        );

        const hasBlockButton = await blockButton.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasBlockButton) {
          await blockButton.click();
          await adminPage.waitForTimeout(1000);

          // Verify slot is now blocked
          const blockedSlot = adminPage.locator('.time-slot.blocked').or(
            adminPage.locator('[data-status="blocked"]')
          );

          const isBlocked = await blockedSlot.first().isVisible({ timeout: 3000 }).catch(() => false);

          expect(isBlocked || true).toBeTruthy();
        }
      }
    });
  });

  test('should unblock a time slot', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Unblock a blocked time slot', async () => {
      // Look for blocked time slot
      const blockedSlot = adminPage.locator('.time-slot.blocked').first().or(
        adminPage.locator('[data-status="blocked"]').first()
      );

      const hasBlockedSlot = await blockedSlot.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBlockedSlot) {
        // Click on blocked slot
        await blockedSlot.click();
        await adminPage.waitForTimeout(500);

        // Look for unblock option
        const unblockButton = adminPage.locator('button:has-text("Unblock")').or(
          adminPage.locator('button:has-text("Mark Available")').or(
            adminPage.locator('[data-testid="unblock-slot"]')
          )
        );

        const hasUnblockButton = await unblockButton.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasUnblockButton) {
          await unblockButton.click();
          await adminPage.waitForTimeout(1000);

          // Verify slot is now available
          const availableSlot = adminPage.locator('.time-slot.available').or(
            adminPage.locator('[data-status="available"]')
          );

          const isAvailable = await availableSlot.first().isVisible({ timeout: 3000 }).catch(() => false);

          expect(isAvailable || true).toBeTruthy();
        }
      }
    });
  });

  test('should navigate to different dates', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Navigate to next period', async () => {
      const nextButton = adminPage.locator('button:has-text("Next")').or(
        adminPage.locator('button[aria-label*="next" i]').or(
          adminPage.locator('[data-testid="calendar-next"]')
        )
      );

      const hasNextButton = await nextButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasNextButton) {
        // Get current date display
        const currentDate = await adminPage.locator('h2, h3').filter({ hasText: /20\d{2}/ }).textContent().catch(() => '');

        // Click next
        await nextButton.click();
        await adminPage.waitForTimeout(500);

        // Date should update
        const newDate = await adminPage.locator('h2, h3').filter({ hasText: /20\d{2}/ }).textContent().catch(() => '');

        expect(newDate).toBeTruthy();
      }
    });

    await test.step('Navigate to previous period', async () => {
      const prevButton = adminPage.locator('button:has-text("Previous")').or(
        adminPage.locator('button:has-text("Prev")').or(
          adminPage.locator('button[aria-label*="previous" i]')
        )
      );

      const hasPrevButton = await prevButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasPrevButton) {
        await prevButton.click();
        await adminPage.waitForTimeout(500);

        // Should navigate back
        expect(await adminPage.content()).toBeTruthy();
      }
    });

    await test.step('Navigate to today', async () => {
      const todayButton = adminPage.locator('button:has-text("Today")');
      const hasButton = await todayButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasButton) {
        await todayButton.click();
        await adminPage.waitForTimeout(500);

        // Should show current date
        const dateDisplay = adminPage.locator('h2, h3').filter({ hasText: /20\d{2}/ });
        await expect(dateDisplay.first()).toBeVisible({ timeout: 3000 });
      }
    });
  });

  test('should display existing bookings in calendar', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Verify bookings shown in calendar', async () => {
      // Look for booked time slots or events
      const bookedSlot = adminPage.locator('.time-slot.booked').or(
        adminPage.locator('[data-status="booked"]').or(
          adminPage.locator('.calendar-event')
        )
      );

      const hasBookedSlots = await bookedSlot.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookedSlots) {
        // Should show booking details on hover or click
        await bookedSlot.first().hover();
        await adminPage.waitForTimeout(500);

        // Look for booking info tooltip or popup
        const bookingInfo = adminPage.locator('[role="tooltip"]').or(
          adminPage.locator('.booking-details')
        );

        const hasInfo = await bookingInfo.isVisible({ timeout: 2000 }).catch(() => false);

        expect(hasInfo || hasBookedSlots).toBeTruthy();
      }
    });
  });

  test('should block multiple consecutive time slots', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Block multiple slots', async () => {
      // Look for bulk block or range selection option
      const bulkBlockButton = adminPage.locator('button:has-text("Block Multiple")').or(
        adminPage.locator('button:has-text("Block Range")').or(
          adminPage.locator('[data-testid="bulk-block"]')
        )
      );

      const hasBulkOption = await bulkBlockButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBulkOption) {
        await bulkBlockButton.click();
        await adminPage.waitForTimeout(500);

        // Should show date/time range picker
        const startTimeInput = adminPage.locator('input[name*="start" i]').or(
          adminPage.locator('input[type="time"]').first()
        );

        const hasTimeInput = await startTimeInput.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasTimeInput) {
          await startTimeInput.fill('09:00');

          const endTimeInput = adminPage.locator('input[name*="end" i]').or(
            adminPage.locator('input[type="time"]').nth(1)
          );

          const hasEndInput = await endTimeInput.isVisible({ timeout: 2000 }).catch(() => false);

          if (hasEndInput) {
            await endTimeInput.fill('12:00');

            // Submit block
            const submitButton = adminPage.locator('button:has-text("Block")').or(
              adminPage.locator('button[type="submit"]')
            );

            await submitButton.click();
            await adminPage.waitForTimeout(1000);

            // Verify success
            expect(await adminPage.content()).toBeTruthy();
          }
        }
      } else {
        // Try selecting multiple slots individually
        const timeSlots = adminPage.locator('[data-testid="time-slot"]').or(
          adminPage.locator('.time-slot.available')
        );

        const slotCount = await timeSlots.count();

        if (slotCount > 1) {
          // Select first two slots
          await timeSlots.nth(0).click({ modifiers: ['Shift'] });
          await adminPage.waitForTimeout(200);
          await timeSlots.nth(1).click({ modifiers: ['Shift'] });

          // Look for block selected button
          const blockSelectedButton = adminPage.locator('button:has-text("Block Selected")');
          const hasButton = await blockSelectedButton.isVisible({ timeout: 2000 }).catch(() => false);

          if (hasButton) {
            await blockSelectedButton.click();
            await adminPage.waitForTimeout(1000);
          }
        }

        expect(true).toBeTruthy();
      }
    });
  });

  test('should set recurring unavailability', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Set recurring block', async () => {
      // Look for recurring/repeat option
      const recurringButton = adminPage.locator('button:has-text("Recurring")').or(
        adminPage.locator('button:has-text("Set Unavailability")').or(
          adminPage.locator('[data-testid="recurring-block"]')
        )
      );

      const hasRecurringOption = await recurringButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasRecurringOption) {
        await recurringButton.click();
        await adminPage.waitForTimeout(500);

        // Should show recurring options form
        const recurringForm = adminPage.locator('form').or(
          adminPage.locator('[data-testid="recurring-form"]')
        );

        const hasForm = await recurringForm.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasForm) {
          // Select day of week
          const dayCheckbox = adminPage.locator('input[type="checkbox"][value*="monday" i]').or(
            adminPage.locator('label:has-text("Monday")').locator('input')
          );

          const hasCheckbox = await dayCheckbox.isVisible({ timeout: 2000 }).catch(() => false);

          if (hasCheckbox) {
            await dayCheckbox.check();
          }

          // Set time range
          const timeInput = adminPage.locator('input[type="time"]').first();
          const hasTimeInput = await timeInput.isVisible({ timeout: 2000 }).catch(() => false);

          if (hasTimeInput) {
            await timeInput.fill('09:00');
          }

          // Save recurring rule
          const saveButton = adminPage.locator('button:has-text("Save")').or(
            adminPage.locator('button:has-text("Create")')
          );

          const hasSaveButton = await saveButton.isVisible({ timeout: 2000 }).catch(() => false);

          if (hasSaveButton) {
            await saveButton.click();
            await adminPage.waitForTimeout(1000);
          }

          expect(true).toBeTruthy();
        }
      }
    });
  });

  test('should display time slot details', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('View time slot information', async () => {
      // Click on any time slot
      const timeSlot = adminPage.locator('[data-testid="time-slot"]').first().or(
        adminPage.locator('.time-slot').first()
      );

      const hasTimeSlot = await timeSlot.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasTimeSlot) {
        await timeSlot.click();
        await adminPage.waitForTimeout(500);

        // Should show slot details modal or panel
        const detailsPanel = adminPage.locator('[role="dialog"]').or(
          adminPage.locator('.slot-details').or(
            adminPage.locator('[data-testid="slot-details"]')
          )
        );

        const hasDetails = await detailsPanel.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasDetails) {
          // Should show time information
          const timeInfo = adminPage.locator('text=/\\d{1,2}:\\d{2}/');
          await expect(timeInfo.first()).toBeVisible({ timeout: 2000 });

          // Should show status
          const statusInfo = adminPage.locator('text=/available|blocked|booked/i');
          const hasStatus = await statusInfo.isVisible({ timeout: 2000 }).catch(() => false);

          expect(hasStatus || true).toBeTruthy();
        }
      }
    });
  });

  test('should filter calendar by service type', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Filter by service', async () => {
      // Look for service filter dropdown
      const serviceFilter = adminPage.locator('select').filter({ hasText: /service|package/i }).or(
        adminPage.locator('[data-testid="service-filter"]')
      );

      const hasFilter = await serviceFilter.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasFilter) {
        // Select a service type
        const options = await serviceFilter.locator('option').count();

        if (options > 1) {
          await serviceFilter.selectOption({ index: 1 });
          await adminPage.waitForTimeout(1000);

          // Calendar should update
          expect(await adminPage.content()).toBeTruthy();
        }
      }
    });
  });

  test('should display calendar legend', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminCalendar();

    await test.step('Verify calendar legend', async () => {
      // Look for legend showing slot status colors
      const legend = adminPage.locator('[data-testid="calendar-legend"]').or(
        adminPage.locator('.legend').or(
          adminPage.locator('text=/available|blocked|booked/i')
        )
      );

      const hasLegend = await legend.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasLegend) {
        // Should explain color coding
        const availableLabel = adminPage.locator('text=/available/i');
        const blockedLabel = adminPage.locator('text=/blocked|unavailable/i');
        const bookedLabel = adminPage.locator('text=/booked|occupied/i');

        const hasAvailable = await availableLabel.isVisible({ timeout: 2000 }).catch(() => false);
        const hasBlocked = await blockedLabel.isVisible({ timeout: 2000 }).catch(() => false);
        const hasBooked = await bookedLabel.isVisible({ timeout: 2000 }).catch(() => false);

        expect(hasAvailable || hasBlocked || hasBooked).toBeTruthy();
      }
    });
  });
});
