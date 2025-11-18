/**
 * Admin booking management API functions
 */
import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import type { Booking, PaginatedResponse } from "@/types";

interface BookingListParams {
  page?: number;
  pageSize?: number;
  status?: string;
  startDate?: string;
  endDate?: string;
  locationId?: string;
}

interface BookingUpdateData {
  bookingDate?: string;
  bookingTime?: string;
  locationId?: string;
  numBrides?: number;
  numMaids?: number;
  numMothers?: number;
  numOthers?: number;
  weddingTheme?: string;
  specialRequests?: string;
  adminNotes?: string;
}

interface DepositUpdateData {
  depositPaid: boolean;
  adminNotes?: string;
}

interface StatusUpdateData {
  status: "pending" | "confirmed" | "deposit_paid" | "completed" | "cancelled";
  adminNotes?: string;
}

/**
 * Fetch all bookings with filters (admin only)
 */
export async function fetchAdminBookings(
  params: BookingListParams,
  token: string
): Promise<PaginatedResponse<Booking>> {
  const queryParams: Record<string, string | number> = {};

  if (params.page) queryParams.page = params.page;
  if (params.pageSize) queryParams.page_size = params.pageSize;
  if (params.status) queryParams.status = params.status;
  if (params.startDate) queryParams.startDate = params.startDate;
  if (params.endDate) queryParams.endDate = params.endDate;
  if (params.locationId) queryParams.locationId = params.locationId;

  const response = await axios.get<PaginatedResponse<Booking>>(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.LIST}`,
    {
      params: queryParams,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Get a specific booking by ID (admin only)
 */
export async function fetchAdminBooking(
  bookingId: string,
  token: string
): Promise<Booking> {
  const response = await axios.get<Booking>(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.DETAIL(bookingId)}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Update a booking (admin only)
 */
export async function updateAdminBooking(
  bookingId: string,
  data: BookingUpdateData,
  token: string
): Promise<Booking> {
  const response = await axios.put<Booking>(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.UPDATE(bookingId)}`,
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Mark deposit as paid/unpaid (admin only)
 */
export async function updateBookingDeposit(
  bookingId: string,
  data: DepositUpdateData,
  token: string
): Promise<Booking> {
  const response = await axios.put<Booking>(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.DEPOSIT(bookingId)}`,
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Update booking status (admin only)
 */
export async function updateBookingStatus(
  bookingId: string,
  data: StatusUpdateData,
  token: string
): Promise<Booking> {
  const response = await axios.put<Booking>(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.STATUS(bookingId)}`,
    data,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Cancel a booking (admin only)
 */
export async function cancelAdminBooking(
  bookingId: string,
  adminNotes: string | undefined,
  token: string
): Promise<void> {
  const params = adminNotes ? { admin_notes: adminNotes } : {};

  await axios.delete(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.CANCEL(bookingId)}`,
    {
      params,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
}

/**
 * Export bookings to CSV (admin only)
 */
export async function exportBookingsCSV(
  params: Omit<BookingListParams, "page" | "pageSize">,
  token: string
): Promise<Blob> {
  const queryParams: Record<string, string> = {};

  if (params.status) queryParams.status = params.status;
  if (params.startDate) queryParams.startDate = params.startDate;
  if (params.endDate) queryParams.endDate = params.endDate;
  if (params.locationId) queryParams.locationId = params.locationId;

  const response = await axios.get(
    `${API_BASE_URL}${API_ENDPOINTS.ADMIN_BOOKINGS.EXPORT_CSV}`,
    {
      params: queryParams,
      headers: {
        Authorization: `Bearer ${token}`,
      },
      responseType: "blob",
    }
  );

  return response.data;
}
