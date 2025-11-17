/**
 * API configuration and constants
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    GOOGLE_LOGIN: "/auth/google",
    LOGOUT: "/auth/logout",
    ME: "/auth/me",
  },
  // Products
  PRODUCTS: {
    LIST: "/products",
    DETAIL: (id: string) => `/products/${id}`,
    SEARCH: "/products/search",
    FEATURED: "/products/featured",
  },
  // Brands
  BRANDS: {
    LIST: "/brands",
    DETAIL: (id: string) => `/brands/${id}`,
  },
  // Categories
  CATEGORIES: {
    LIST: "/categories",
    DETAIL: (id: string) => `/categories/${id}`,
    HIERARCHY: "/categories/hierarchy",
  },
  // Services
  SERVICES: {
    LIST: "/api/services",
    DETAIL: (id: string) => `/api/services/${id}`,
  },
  // Bookings
  BOOKINGS: {
    CREATE: "/api/bookings",
    LIST: "/api/bookings",
    DETAIL: (id: string) => `/api/bookings/${id}`,
    AVAILABILITY: "/api/bookings/availability",
    CANCEL: (id: string) => `/api/bookings/${id}/cancel`,
  },
  // Orders
  ORDERS: {
    CREATE: "/orders",
    LIST: "/orders",
    DETAIL: (id: string) => `/orders/${id}`,
    MY_ORDERS: "/orders/me",
  },
  // Cart
  CART: {
    GET: "/cart",
    ADD_ITEM: "/cart/items",
    UPDATE_ITEM: (itemId: string) => `/cart/items/${itemId}`,
    REMOVE_ITEM: (itemId: string) => `/cart/items/${itemId}`,
    CLEAR: "/cart/clear",
  },
  // Promo Codes
  PROMO_CODES: {
    VALIDATE: "/promo-codes/validate",
  },
  // Reviews
  REVIEWS: {
    CREATE: "/reviews",
    LIST: (productId: string) => `/products/${productId}/reviews`,
  },
  // Content
  CONTENT: {
    TESTIMONIALS: "/testimonials",
    GALLERY: "/gallery",
  },
} as const;

export const HTTP_METHODS = {
  GET: "GET",
  POST: "POST",
  PUT: "PUT",
  PATCH: "PATCH",
  DELETE: "DELETE",
} as const;
