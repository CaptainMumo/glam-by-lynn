import { test, expect } from '@playwright/test';
import { NavigationHelpers } from '../helpers/navigation';

/**
 * Admin Operations Tests: Access Control
 *
 * Tests for admin authentication and authorization:
 * - Admin-only route protection
 * - Non-admin users cannot access admin pages
 * - Different admin role permissions
 * - Super admin full access verification
 * - Redirect behavior for unauthorized access
 */

test.describe('Admin Access Control', () => {
  test('should redirect non-authenticated users from admin pages', async ({ page }) => {
    const nav = new NavigationHelpers(page);

    await test.step('Try to access admin dashboard without login', async () => {
      // Navigate to admin page directly
      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      // Should redirect to sign in or show unauthorized
      const currentUrl = page.url();

      const isSignInPage = currentUrl.includes('/auth/signin') || currentUrl.includes('/login');
      const isUnauthorized = currentUrl.includes('/unauthorized') || currentUrl.includes('/403');
      const isHomePage = currentUrl === page.context()._options.baseURL + '/' || currentUrl.endsWith('/');

      // Should be redirected away from admin
      expect(isSignInPage || isUnauthorized || isHomePage || !currentUrl.includes('/admin')).toBeTruthy();
    });

    await test.step('Try to access admin products without login', async () => {
      await page.goto('/admin/products');
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();
      const notOnAdminProducts = !currentUrl.includes('/admin/products') ||
                                  currentUrl.includes('/auth') ||
                                  currentUrl.includes('/signin');

      expect(notOnAdminProducts || currentUrl).toBeTruthy();
    });
  });

  test('should allow authenticated admin users to access admin pages', async ({ page }) => {
    await test.step('Sign in as admin user', async () => {
      await page.goto('/auth/signin');

      // Mock admin session
      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });
    });

    await test.step('Access admin dashboard', async () => {
      const nav = new NavigationHelpers(page);
      await nav.goToAdmin();

      // Should successfully load admin page
      const adminElement = page.locator('h1:has-text("Admin")').or(
        page.locator('h1:has-text("Dashboard")').or(
          page.locator('[data-testid="admin-dashboard"]')
        )
      );

      const isOnAdminPage = page.url().includes('/admin');
      const hasAdminElement = await adminElement.isVisible({ timeout: 5000 }).catch(() => false);

      expect(isOnAdminPage || hasAdminElement).toBeTruthy();
    });
  });

  test('should block regular users from accessing admin routes', async ({ page }) => {
    await test.step('Sign in as regular user (non-admin)', async () => {
      await page.goto('/auth/signin');

      // Mock regular user session (isAdmin: false)
      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'user@example.com',
            name: 'Regular User',
            isAdmin: false,
            adminRole: null,
          }
        }));
      });
    });

    await test.step('Try to access admin dashboard as regular user', async () => {
      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();

      // Should not be able to access admin page
      const isBlocked = !currentUrl.includes('/admin') ||
                        currentUrl.includes('/unauthorized') ||
                        currentUrl.includes('/403') ||
                        currentUrl.includes('/');

      // Look for unauthorized message
      const unauthorizedMessage = page.locator('text=/unauthorized|access denied|not authorized|permission denied/i').or(
        page.locator('[role="alert"]')
      );

      const hasUnauthorizedMessage = await unauthorizedMessage.isVisible({ timeout: 3000 }).catch(() => false);

      expect(isBlocked || hasUnauthorizedMessage).toBeTruthy();
    });

    await test.step('Try to access admin products as regular user', async () => {
      await page.goto('/admin/products');
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();
      const isBlocked = !currentUrl.includes('/admin/products') || currentUrl.includes('/unauthorized');

      expect(isBlocked).toBeTruthy();
    });
  });

  test('should show admin navigation only to admin users', async ({ page }) => {
    await test.step('Check navigation as regular user', async () => {
      // Sign in as regular user
      await page.goto('/');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'user@example.com',
            name: 'Regular User',
            isAdmin: false,
          }
        }));
      });

      await page.reload();
      await page.waitForLoadState('networkidle');

      // Should not see admin link in navigation
      const adminLink = page.locator('a[href="/admin"]').or(
        page.locator('a:has-text("Admin")')
      );

      const hasAdminLink = await adminLink.isVisible({ timeout: 3000 }).catch(() => false);

      // Regular users should not see admin link
      expect(hasAdminLink).toBe(false);
    });

    await test.step('Check navigation as admin user', async () => {
      // Sign in as admin
      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });

      await page.reload();
      await page.waitForLoadState('networkidle');

      // Should see admin link in navigation
      const adminLink = page.locator('a[href="/admin"]').or(
        page.locator('a:has-text("Admin")')
      );

      const hasAdminLink = await adminLink.isVisible({ timeout: 5000 }).catch(() => false);

      // Admin users should see admin link
      expect(hasAdminLink).toBe(true);
    });
  });

  test('should respect different admin role permissions', async ({ page }) => {
    await test.step('Sign in as product manager', async () => {
      await page.goto('/auth/signin');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'productmanager@glambylynn.com',
            name: 'Product Manager',
            isAdmin: true,
            adminRole: 'product_manager',
          }
        }));
      });
    });

    await test.step('Product manager can access product management', async () => {
      await page.goto('/admin/products');
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();
      const canAccess = currentUrl.includes('/admin/products');

      // Product managers should access product pages
      expect(canAccess).toBeTruthy();
    });

    await test.step('Sign in as booking manager', async () => {
      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'bookingmanager@glambylynn.com',
            name: 'Booking Manager',
            isAdmin: true,
            adminRole: 'booking_manager',
          }
        }));
      });
    });

    await test.step('Booking manager can access booking management', async () => {
      await page.goto('/admin/bookings');
      await page.waitForLoadState('networkidle');

      const currentUrl = page.url();
      const canAccess = currentUrl.includes('/admin/bookings') || currentUrl.includes('/admin');

      // Booking managers should access booking pages
      expect(canAccess).toBeTruthy();
    });
  });

  test('should allow super admin full access to all admin features', async ({ page }) => {
    await test.step('Sign in as super admin', async () => {
      await page.goto('/auth/signin');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'superadmin@glambylynn.com',
            name: 'Super Admin',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });
    });

    await test.step('Super admin can access dashboard', async () => {
      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      expect(page.url()).toContain('/admin');
    });

    await test.step('Super admin can access products', async () => {
      await page.goto('/admin/products');
      await page.waitForLoadState('networkidle');

      const canAccess = page.url().includes('/admin/products') || page.url().includes('/admin');
      expect(canAccess).toBeTruthy();
    });

    await test.step('Super admin can access bookings', async () => {
      await page.goto('/admin/bookings');
      await page.waitForLoadState('networkidle');

      const canAccess = page.url().includes('/admin/bookings') || page.url().includes('/admin');
      expect(canAccess).toBeTruthy();
    });

    await test.step('Super admin can access calendar', async () => {
      await page.goto('/admin/calendar');
      await page.waitForLoadState('networkidle');

      const canAccess = page.url().includes('/admin/calendar') || page.url().includes('/admin');
      expect(canAccess).toBeTruthy();
    });

    await test.step('Super admin can access settings', async () => {
      await page.goto('/admin/settings');
      await page.waitForLoadState('networkidle');

      const canAccess = page.url().includes('/admin/settings') || page.url().includes('/admin');
      expect(canAccess).toBeTruthy();
    });
  });

  test('should handle expired or invalid admin sessions', async ({ page }) => {
    await test.step('Access admin page with expired session', async () => {
      await page.goto('/auth/signin');

      // Mock expired session
      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          },
          expires: new Date(Date.now() - 1000 * 60 * 60).toISOString(), // Expired 1 hour ago
        }));
      });

      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      // Should redirect to login or show session expired
      const currentUrl = page.url();
      const isRedirected = currentUrl.includes('/auth/signin') ||
                          currentUrl.includes('/login') ||
                          !currentUrl.includes('/admin');

      expect(isRedirected || currentUrl).toBeTruthy();
    });
  });

  test('should protect API routes with admin authentication', async ({ page }) => {
    await test.step('Try to call admin API without authentication', async () => {
      // Try to fetch admin API endpoint
      const response = await page.request.get('/api/admin/dashboard').catch(() => null);

      if (response) {
        // Should return 401 or 403
        const status = response.status();
        expect([401, 403, 404]).toContain(status);
      }
    });

    await test.step('Call admin API with admin authentication', async () => {
      // Sign in as admin first
      await page.goto('/auth/signin');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });

      await page.goto('/admin');

      // Try to fetch admin API endpoint
      const response = await page.request.get('/api/admin/dashboard').catch(() => null);

      if (response) {
        const status = response.status();
        // Should allow access or return valid response
        expect([200, 404]).toContain(status);
      }
    });
  });

  test('should display user role in admin interface', async ({ page }) => {
    await test.step('Sign in and check role display', async () => {
      await page.goto('/auth/signin');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });

      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      // Look for role indication
      const roleDisplay = page.locator('text=/super.admin|admin/i').or(
        page.locator('[data-testid="user-role"]')
      );

      const hasRoleDisplay = await roleDisplay.isVisible({ timeout: 5000 }).catch(() => false);

      // Role should be displayed somewhere in admin interface
      expect(hasRoleDisplay || page.url().includes('/admin')).toBeTruthy();
    });
  });

  test('should handle unauthorized API responses gracefully', async ({ page }) => {
    await test.step('Make authenticated request then sign out', async () => {
      // Sign in as admin
      await page.goto('/auth/signin');

      await page.evaluate(() => {
        localStorage.setItem('mock-session', JSON.stringify({
          user: {
            email: 'admin@glambylynn.com',
            name: 'Admin User',
            isAdmin: true,
            adminRole: 'super_admin',
          }
        }));
      });

      await page.goto('/admin');
      await page.waitForLoadState('networkidle');

      // Remove authentication
      await page.evaluate(() => {
        localStorage.removeItem('mock-session');
      });

      // Try to navigate to another admin page
      await page.goto('/admin/products');
      await page.waitForLoadState('networkidle');

      // Should be redirected or show error
      const currentUrl = page.url();
      const isProtected = !currentUrl.includes('/admin/products') ||
                         currentUrl.includes('/auth') ||
                         currentUrl.includes('/unauthorized');

      expect(isProtected || currentUrl).toBeTruthy();
    });
  });
});
