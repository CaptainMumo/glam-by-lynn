import { Page } from '@playwright/test';

/**
 * Form filling helpers for checkout and booking forms
 */

export interface GuestInfo {
  name: string;
  email: string;
  phone: string;
}

export interface ShippingAddress {
  street: string;
  city: string;
  county?: string;
  postalCode?: string;
}

export class FormHelpers {
  constructor(private page: Page) {}

  /**
   * Fill guest information (name, email, phone)
   */
  async fillGuestInfo(guestInfo: GuestInfo) {
    await this.page.fill('input[name="name"], input[placeholder*="name" i]', guestInfo.name);
    await this.page.fill('input[name="email"], input[type="email"]', guestInfo.email);
    await this.page.fill('input[name="phone"], input[type="tel"]', guestInfo.phone);
  }

  /**
   * Fill shipping address
   */
  async fillShippingAddress(address: ShippingAddress) {
    await this.page.fill('input[name="street"], input[placeholder*="street" i], textarea[name="address"]', address.street);
    await this.page.fill('input[name="city"], input[placeholder*="city" i]', address.city);

    if (address.county) {
      await this.page.fill('input[name="county"], input[placeholder*="county" i]', address.county);
    }

    if (address.postalCode) {
      await this.page.fill('input[name="postalCode"], input[placeholder*="postal" i]', address.postalCode);
    }
  }

  /**
   * Select payment method
   */
  async selectPaymentMethod(method: 'mpesa' | 'card' | 'cash') {
    const paymentSelector = `input[value="${method}"], button:has-text("${method}")`;
    await this.page.click(paymentSelector, { force: true });
  }

  /**
   * Fill M-Pesa phone number
   */
  async fillMpesaPhone(phone: string) {
    await this.page.fill('input[placeholder*="M-Pesa" i], input[name="mpesaPhone"]', phone);
  }

  /**
   * Submit form
   */
  async submitForm(buttonText: string = 'Submit') {
    const submitButton = this.page.locator(`button:has-text("${buttonText}")`).or(
      this.page.locator('button[type="submit"]')
    );
    await submitButton.click();
  }

  /**
   * Wait for form submission and confirmation
   */
  async waitForConfirmation(timeout: number = 10000) {
    await this.page.waitForURL(/\/confirmation|\/success/, { timeout });
  }
}
