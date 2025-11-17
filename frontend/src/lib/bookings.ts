/**
 * Bookings API client
 * Functions to interact with the bookings backend API
 */

import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { TransportLocation, Booking } from "@/types";

/**
 * Fetch all active transport locations
 */
export async function getTransportLocations(): Promise<TransportLocation[]> {
  const response = await fetch(`${API_BASE_URL}/api/services/locations`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch transport locations: ${response.statusText}`);
  }

  const data = await response.json();
  return data;
}

/**
 * Check availability for a date range
 */
export async function checkAvailability(
  startDate: string,
  endDate?: string,
  days: number = 7
): Promise<any> {
  const params = new URLSearchParams({
    start_date: startDate,
    days: days.toString(),
  });

  if (endDate) {
    params.set("end_date", endDate);
  }

  const response = await fetch(
    `${API_BASE_URL}${API_ENDPOINTS.BOOKINGS.AVAILABILITY}?${params}`,
    {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch availability: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create a new booking
 */
export async function createBooking(
  bookingData: {
    package_id: string;
    booking_date: string;
    booking_time: string;
    location_id: string;
    num_brides: number;
    num_maids: number;
    num_mothers: number;
    num_others: number;
    wedding_theme?: string;
    special_requests?: string;
    guest_email?: string;
    guest_name?: string;
    guest_phone?: string;
  },
  token?: string
): Promise<Booking> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BOOKINGS.CREATE}`, {
    method: "POST",
    headers,
    body: JSON.stringify(bookingData),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create booking: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate booking price
 */
export function calculateBookingPrice(
  baseBridePrice: number = 0,
  baseMaidPrice: number = 0,
  baseMotherPrice: number = 0,
  baseOtherPrice: number = 0,
  numBrides: number = 0,
  numMaids: number = 0,
  numMothers: number = 0,
  numOthers: number = 0,
  transportCost: number = 0
): { subtotal: number; transport: number; total: number; deposit: number } {
  const subtotal =
    baseBridePrice * numBrides +
    baseMaidPrice * numMaids +
    baseMotherPrice * numMothers +
    baseOtherPrice * numOthers;

  const total = subtotal + transportCost;
  const deposit = Math.round(total * 0.5);

  return {
    subtotal,
    transport: transportCost,
    total,
    deposit,
  };
}

/**
 * Get a specific booking by ID
 */
export async function getBookingById(bookingId: string, token?: string): Promise<Booking> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.BOOKINGS.DETAIL(bookingId)}`, {
    method: "GET",
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch booking: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Format currency for display (KSh)
 */
export function formatCurrency(amount: number): string {
  return `KSh ${amount.toLocaleString()}`;
}

/**
 * Format date for display
 */
export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Format time for display
 */
export function formatTime(timeStr: string): string {
  const [hours, minutes] = timeStr.split(":");
  const hour = parseInt(hours);
  const ampm = hour >= 12 ? "PM" : "AM";
  const displayHour = hour % 12 || 12;
  return `${displayHour}:${minutes} ${ampm}`;
}
