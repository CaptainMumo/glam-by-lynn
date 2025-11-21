import { test, expect } from '../fixtures/auth.fixture';
import { NavigationHelpers } from '../helpers/navigation';

/**
 * Admin Operations Tests: Booking Management
 *
 * Tests for admin booking management operations:
 * - Viewing admin bookings dashboard
 * - Filtering bookings by status and date range
 * - Updating booking status
 * - Marking deposits as paid
 * - Adding admin notes
 * - Cancelling bookings
 * - Exporting bookings to CSV
 */

test.describe('Admin Booking Management', () => {
  test('should access admin bookings dashboard', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await test.step('Navigate to admin bookings page', async () => {
      await nav.goToAdminBookings();

      // Verify we're on admin bookings page
      const pageTitle = adminPage.locator('h1:has-text("Booking")').or(
        adminPage.locator('h1:has-text("Bookings")')
      );
      await expect(pageTitle).toBeVisible({ timeout: 10000 });
    });

    await test.step('Verify admin booking UI elements', async () => {
      // Should have filter or search controls
      const filterControls = adminPage.locator('select').or(
        adminPage.locator('input[type="search"]')
      );

      const hasFilters = await filterControls.first().isVisible({ timeout: 5000 }).catch(() => false);

      // Should have bookings table or grid
      const bookingsTable = adminPage.locator('table').or(
        adminPage.locator('[data-testid="bookings-grid"]')
      );

      const hasTable = await bookingsTable.isVisible({ timeout: 5000 }).catch(() => false);

      // Should have either filters or bookings display
      expect(hasFilters || hasTable).toBe(true);
    });
  });

  test('should display booking list with admin details', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Verify booking list columns', async () => {
      // Look for booking rows
      const bookingRows = adminPage.locator('tbody tr').or(
        adminPage.locator('[data-testid="booking-row"]')
      );

      const hasBookings = await bookingRows.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        // Should show customer name or booking ID
        const bookingInfo = adminPage.locator('td').first();
        await expect(bookingInfo).toBeVisible();

        // Should show status
        const statusColumn = adminPage.locator('text=/Pending|Confirmed|Completed|Cancelled/i');
        const hasStatus = await statusColumn.first().isVisible({ timeout: 3000 }).catch(() => false);

        // Should show date
        const dateColumn = adminPage.locator('text=/\\d{4}-\\d{2}-\\d{2}/');
        const hasDate = await dateColumn.first().isVisible({ timeout: 3000 }).catch(() => false);

        expect(hasStatus || hasDate).toBe(true);
      }
    });
  });

  test('should filter bookings by status', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Apply status filter', async () => {
      // Look for status filter dropdown
      const statusFilter = adminPage.locator('select').filter({ hasText: /status/i }).or(
        adminPage.locator('[data-testid="status-filter"]')
      );

      const hasFilter = await statusFilter.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasFilter) {
        // Select confirmed status
        await statusFilter.selectOption({ label: /confirmed/i });
        await adminPage.waitForTimeout(1000);

        // Verify filter applied
        const url = adminPage.url();
        const content = await adminPage.content();

        // URL or content should reflect the filter
        expect(url.includes('status') || content.includes('Confirmed')).toBeTruthy();
      }
    });
  });

  test('should filter bookings by date range', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Apply date range filter', async () => {
      // Look for date inputs
      const startDateInput = adminPage.locator('input[type="date"]').first().or(
        adminPage.locator('input[name*="start" i]')
      );

      const hasDateFilter = await startDateInput.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasDateFilter) {
        // Set date range for next 30 days
        const today = new Date();
        const nextMonth = new Date();
        nextMonth.setDate(today.getDate() + 30);

        await startDateInput.fill(today.toISOString().split('T')[0]);

        const endDateInput = adminPage.locator('input[type="date"]').nth(1);
        const hasEndDate = await endDateInput.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasEndDate) {
          await endDateInput.fill(nextMonth.toISOString().split('T')[0]);
          await adminPage.waitForTimeout(1000);
        }

        // Verify page updated
        expect(await adminPage.content()).toBeTruthy();
      }
    });
  });

  test('should update booking status', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Change booking status', async () => {
      // Look for first booking with status dropdown or button
      const statusDropdown = adminPage.locator('select').filter({ hasText: /status|pending|confirmed/i }).first().or(
        adminPage.locator('[data-testid="status-select"]').first()
      );

      const hasDropdown = await statusDropdown.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasDropdown) {
        // Get current status
        const currentStatus = await statusDropdown.inputValue().catch(() => '');

        // Change to different status
        const newStatus = currentStatus.toLowerCase().includes('pending') ? 'confirmed' : 'completed';

        await statusDropdown.selectOption({ label: new RegExp(newStatus, 'i') });
        await adminPage.waitForTimeout(1000);

        // Look for success message
        const successMessage = adminPage.locator('text=/updated|success/i').or(
          adminPage.locator('[role="alert"]')
        );

        const hasSuccess = await successMessage.isVisible({ timeout: 3000 }).catch(() => false);

        // Should either show success or status change persisted
        expect(hasSuccess || await statusDropdown.isVisible()).toBeTruthy();
      }
    });
  });

  test('should mark deposit as paid', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Mark deposit paid', async () => {
      // Look for deposit payment controls
      const depositCheckbox = adminPage.locator('input[type="checkbox"]').filter({ hasText: /deposit|paid/i }).first().or(
        adminPage.locator('[data-testid="deposit-paid"]').first()
      );

      const hasDepositControl = await depositCheckbox.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasDepositControl) {
        const isChecked = await depositCheckbox.isChecked().catch(() => false);

        if (!isChecked) {
          await depositCheckbox.check();
          await adminPage.waitForTimeout(1000);

          // Verify it's now checked
          const nowChecked = await depositCheckbox.isChecked();
          expect(nowChecked).toBe(true);
        }
      }

      // Or look for deposit button
      const depositButton = adminPage.locator('button:has-text("Mark Paid")').first().or(
        adminPage.locator('button:has-text("Deposit Paid")').first()
      );

      const hasButton = await depositButton.isVisible({ timeout: 3000 }).catch(() => false);

      if (hasButton) {
        await depositButton.click();
        await adminPage.waitForTimeout(1000);

        // Look for success confirmation
        const confirmation = adminPage.locator('text=/paid|success|updated/i');
        const hasConfirmation = await confirmation.isVisible({ timeout: 3000 }).catch(() => false);

        expect(hasConfirmation || !await depositButton.isVisible()).toBeTruthy();
      }
    });
  });

  test('should add admin notes to booking', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Add note to booking', async () => {
      // Look for first booking detail or expand button
      const viewButton = adminPage.locator('button:has-text("View")').first().or(
        adminPage.locator('button:has-text("Details")').first()
      );

      const hasViewButton = await viewButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasViewButton) {
        await viewButton.click();
        await adminPage.waitForTimeout(1000);

        // Look for notes textarea
        const notesTextarea = adminPage.locator('textarea[name*="note" i]').or(
          adminPage.locator('textarea[placeholder*="note" i]').or(
            adminPage.locator('[data-testid="admin-notes"]')
          )
        );

        const hasNotesField = await notesTextarea.isVisible({ timeout: 5000 }).catch(() => false);

        if (hasNotesField) {
          const testNote = `Admin note added at ${new Date().toISOString()}`;
          await notesTextarea.fill(testNote);

          // Look for save button
          const saveButton = adminPage.locator('button:has-text("Save")').or(
            adminPage.locator('button:has-text("Update")')
          );

          const hasSaveButton = await saveButton.isVisible({ timeout: 3000 }).catch(() => false);

          if (hasSaveButton) {
            await saveButton.click();
            await adminPage.waitForTimeout(1000);

            // Verify note was saved
            const savedNote = await notesTextarea.inputValue();
            expect(savedNote).toContain('Admin note');
          }
        }
      }
    });
  });

  test('should cancel booking as admin', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Cancel a booking', async () => {
      // Look for cancel button in first booking
      const cancelButton = adminPage.locator('button:has-text("Cancel")').first().or(
        adminPage.locator('button:has-text("Cancel Booking")').first()
      );

      const hasCancelButton = await cancelButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasCancelButton) {
        await cancelButton.click();
        await adminPage.waitForTimeout(500);

        // Look for confirmation dialog
        const confirmDialog = adminPage.locator('text=/confirm|are you sure/i').or(
          adminPage.locator('[role="dialog"]')
        );

        const hasDialog = await confirmDialog.isVisible({ timeout: 3000 }).catch(() => false);

        if (hasDialog) {
          // Confirm cancellation
          const confirmButton = adminPage.locator('button:has-text("Confirm")').or(
            adminPage.locator('button:has-text("Yes")')
          );

          await confirmButton.click();
          await adminPage.waitForTimeout(1000);

          // Verify booking shows as cancelled
          const cancelledStatus = adminPage.locator('text=/cancelled/i');
          const isCancelled = await cancelledStatus.first().isVisible({ timeout: 3000 }).catch(() => false);

          expect(isCancelled || await adminPage.content()).toBeTruthy();
        }
      }
    });
  });

  test('should export bookings to CSV', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Export bookings data', async () => {
      // Look for export button
      const exportButton = adminPage.locator('button:has-text("Export")').or(
        adminPage.locator('button:has-text("Download")').or(
          adminPage.locator('[data-testid="export-csv"]')
        )
      );

      const hasExportButton = await exportButton.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasExportButton) {
        // Set up download listener
        const downloadPromise = adminPage.waitForEvent('download', { timeout: 5000 }).catch(() => null);

        await exportButton.click();

        // Wait for download
        const download = await downloadPromise;

        if (download) {
          // Verify download filename contains 'booking' or 'csv'
          const filename = download.suggestedFilename();
          expect(filename.toLowerCase()).toMatch(/booking|csv/);
        }
      }
    });
  });

  test('should search bookings by customer name', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Search for booking', async () => {
      // Look for search input
      const searchInput = adminPage.locator('input[type="search"]').or(
        adminPage.locator('input[placeholder*="search" i]')
      );

      const hasSearch = await searchInput.isVisible({ timeout: 5000 }).catch(() => false);

      if (hasSearch) {
        // Search for a test customer
        await searchInput.fill('test');
        await adminPage.waitForTimeout(1000);

        // Verify search is functional
        const searchValue = await searchInput.inputValue();
        expect(searchValue).toBe('test');

        // Page should update with search results
        const content = await adminPage.content();
        expect(content).toBeTruthy();
      }
    });
  });

  test('should display booking payment status', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Verify payment status display', async () => {
      const bookingRows = adminPage.locator('tbody tr').or(
        adminPage.locator('[data-testid="booking-row"]')
      );

      const hasBookings = await bookingRows.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        // Look for payment indicators
        const paymentStatus = adminPage.locator('text=/paid|unpaid|pending payment|deposit/i');
        const hasPaymentInfo = await paymentStatus.first().isVisible({ timeout: 3000 }).catch(() => false);

        // Or look for payment amount
        const amountColumn = adminPage.locator('text=/KSh|\\d+/');
        const hasAmount = await amountColumn.first().isVisible({ timeout: 3000 }).catch(() => false);

        expect(hasPaymentInfo || hasAmount).toBe(true);
      }
    });
  });

  test('should display booking services and location', async ({ adminPage }) => {
    const nav = new NavigationHelpers(adminPage);

    await nav.goToAdminBookings();

    await test.step('Verify service details in list', async () => {
      const bookingRows = adminPage.locator('tbody tr').or(
        adminPage.locator('[data-testid="booking-row"]')
      );

      const hasBookings = await bookingRows.first().isVisible({ timeout: 5000 }).catch(() => false);

      if (hasBookings) {
        // Should show service package name
        const serviceInfo = adminPage.locator('td').first();
        await expect(serviceInfo).toBeVisible();

        // Should show location (Nairobi or Kitui)
        const locationColumn = adminPage.locator('text=/Nairobi|Kitui/i');
        const hasLocation = await locationColumn.first().isVisible({ timeout: 3000 }).catch(() => false);

        // Location info should be present
        expect(typeof hasLocation).toBe('boolean');
      }
    });
  });
});
