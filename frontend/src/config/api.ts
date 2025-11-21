/**
 * API configuration and constants
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    GOOGLE_LOGIN: "/api/auth/google-login",
    LOGOUT: "/api/auth/logout",
    ME: "/api/auth/me",
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
    LIST: "/api/brands",
    DETAIL: (id: string) => `/api/brands/${id}`,
  },
  // Categories
  CATEGORIES: {
    LIST: "/api/categories",
    DETAIL: (id: string) => `/api/categories/${id}`,
    HIERARCHY: "/api/categories/hierarchy",
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
    CREATE: "/api/orders",
    LIST: "/api/orders",
    DETAIL: (id: string) => `/api/orders/${id}`,
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
    CREATE: (productId: string) => `/api/products/${productId}/reviews`,
    LIST: (productId: string) => `/api/products/${productId}/reviews`,
    SUMMARY: (productId: string) => `/api/products/${productId}/reviews/summary`,
    UPDATE: (reviewId: string) => `/api/reviews/${reviewId}`,
    DELETE: (reviewId: string) => `/api/reviews/${reviewId}`,
    MARK_HELPFUL: (reviewId: string) => `/api/reviews/${reviewId}/helpful`,
  },
  // Admin Reviews
  ADMIN_REVIEWS: {
    UPDATE: (reviewId: string) => `/api/admin/reviews/${reviewId}`,
  },
  // Gallery
  GALLERY: {
    LIST: "/api/gallery",
  },
  // Testimonials
  TESTIMONIALS: {
    LIST: "/api/testimonials",
    FEATURED: "/api/testimonials/featured",
  },
  // Admin - Calendar
  ADMIN_CALENDAR: {
    LIST: "/api/admin/calendar",
    BLOCK: "/api/admin/calendar/block",
    UNBLOCK: (id: string) => `/api/admin/calendar/block/${id}`,
    DETAIL: (id: string) => `/api/admin/calendar/${id}`,
  },
  // Admin - Bookings
  ADMIN_BOOKINGS: {
    LIST: "/api/admin/bookings",
    DETAIL: (id: string) => `/api/admin/bookings/${id}`,
    UPDATE: (id: string) => `/api/admin/bookings/${id}`,
    DEPOSIT: (id: string) => `/api/admin/bookings/${id}/deposit`,
    STATUS: (id: string) => `/api/admin/bookings/${id}/status`,
    CANCEL: (id: string) => `/api/admin/bookings/${id}`,
    EXPORT_CSV: "/api/admin/bookings/export/csv",
  },
} as const;

export const HTTP_METHODS = {
  GET: "GET",
  POST: "POST",
  PUT: "PUT",
  PATCH: "PATCH",
  DELETE: "DELETE",
} as const;
