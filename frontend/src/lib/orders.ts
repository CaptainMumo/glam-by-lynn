/**
 * Orders API client
 * Functions to interact with the orders backend API
 */

import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { Order } from "@/types";

/**
 * Get a specific order by ID
 */
export async function getOrderById(orderId: string, token?: string): Promise<Order> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ORDERS.DETAIL(orderId)}`, {
    method: "GET",
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch order: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get user's orders with pagination
 */
export async function getUserOrders(
  skip: number = 0,
  limit: number = 20
): Promise<{ orders: Order[]; total: number; skip: number; limit: number }> {
  const params = new URLSearchParams({
    skip: skip.toString(),
    limit: limit.toString(),
  });

  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ORDERS.LIST}?${params}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch orders: ${response.statusText}`);
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
 * Format date and time for display
 */
export function formatDateTime(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/**
 * Get status badge variant based on order status
 */
export function getStatusBadgeVariant(
  status: string
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "delivered":
    case "payment_confirmed":
      return "default";
    case "pending":
    case "processing":
      return "secondary";
    case "cancelled":
      return "destructive";
    case "shipped":
      return "outline";
    default:
      return "secondary";
  }
}

/**
 * Format status for display
 */
export function formatStatus(status: string): string {
  return status
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}
