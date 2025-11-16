/**
 * Shared TypeScript type definitions
 */

// User types
export interface User {
  id: string;
  email: string;
  fullName?: string;
  phoneNumber?: string;
  profilePictureUrl?: string;
  googleId?: string;
  isAdmin: boolean;
  adminRole?: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist";
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Product types
export interface Brand {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logoUrl?: string;
  isActive: boolean;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  parentCategoryId?: string;
  description?: string;
  imageUrl?: string;
  displayOrder: number;
  isActive: boolean;
}

export interface Product {
  id: string;
  title: string;
  slug: string;
  description?: string;
  brandId?: string;
  categoryId?: string;
  basePrice: number;
  discountType?: "percentage" | "fixed";
  discountValue?: number;
  sku?: string;
  inventoryCount: number;
  lowStockThreshold: number;
  isActive: boolean;
  isFeatured: boolean;
  tags?: string[];
  metaTitle?: string;
  metaDescription?: string;
  brand?: Brand;
  category?: Category;
  images?: ProductImage[];
  variants?: ProductVariant[];
}

export interface ProductImage {
  id: string;
  productId: string;
  imageUrl: string;
  altText?: string;
  isPrimary: boolean;
  displayOrder: number;
}

export interface ProductVariant {
  id: string;
  productId: string;
  variantType: string;
  variantValue: string;
  priceAdjustment: number;
  inventoryCount: number;
  sku?: string;
  isActive: boolean;
}

// Service types
export interface ServicePackage {
  id: string;
  packageType: "bridal_large" | "bridal_small" | "bride_only" | "regular" | "classes";
  name: string;
  description?: string;
  baseBridePrice?: number;
  baseMaidPrice?: number;
  baseMotherPrice?: number;
  baseOtherPrice?: number;
  maxMaids?: number;
  minMaids?: number;
  includesFacial: boolean;
  durationMinutes?: number;
  isActive: boolean;
  displayOrder: number;
}

export interface TransportLocation {
  id: string;
  locationName: string;
  county?: string;
  transportCost: number;
  isFree: boolean;
  isActive: boolean;
}

// Booking types
export interface Booking {
  id: string;
  bookingNumber: string;
  userId?: string;
  guestEmail?: string;
  guestName?: string;
  guestPhone?: string;
  packageId: string;
  bookingDate: string;
  bookingTime: string;
  locationId: string;
  numBrides: number;
  numMaids: number;
  numMothers: number;
  numOthers: number;
  weddingTheme?: string;
  specialRequests?: string;
  subtotal: number;
  transportCost: number;
  totalAmount: number;
  depositAmount?: number;
  depositPaid: boolean;
  depositPaidAt?: string;
  status: "pending" | "confirmed" | "deposit_paid" | "completed" | "cancelled";
  package?: ServicePackage;
  location?: TransportLocation;
}

// Order types
export interface PromoCode {
  id: string;
  code: string;
  description?: string;
  discountType: "percentage" | "fixed";
  discountValue: number;
  minOrderAmount?: number;
  maxDiscountAmount?: number;
  usageLimit?: number;
  usageCount: number;
  validFrom?: string;
  validUntil?: string;
  isActive: boolean;
}

export interface Order {
  id: string;
  orderNumber: string;
  userId?: string;
  guestEmail?: string;
  guestName?: string;
  guestPhone?: string;
  deliveryCounty?: string;
  deliveryTown?: string;
  deliveryAddress?: string;
  subtotal: number;
  discountAmount: number;
  promoCodeId?: string;
  deliveryFee: number;
  totalAmount: number;
  paymentMethod?: string;
  paymentConfirmed: boolean;
  paymentConfirmedAt?: string;
  status: "pending" | "payment_confirmed" | "processing" | "shipped" | "delivered" | "cancelled";
  trackingNumber?: string;
  orderItems?: OrderItem[];
  promoCode?: PromoCode;
}

export interface OrderItem {
  id: string;
  orderId: string;
  productId?: string;
  productVariantId?: string;
  productTitle: string;
  productSku?: string;
  quantity: number;
  unitPrice: number;
  discount: number;
  totalPrice: number;
}

export interface CartItem {
  id: string;
  cartId: string;
  productId: string;
  productVariantId?: string;
  quantity: number;
  product?: Product;
  productVariant?: ProductVariant;
}

// Content types
export interface Review {
  id: string;
  productId: string;
  userId: string;
  rating: number;
  reviewText?: string;
  isVerifiedPurchase: boolean;
  isApproved: boolean;
  helpfulCount: number;
  adminReply?: string;
  adminReplyAt?: string;
  createdAt: string;
  user?: User;
}

export interface Testimonial {
  id: string;
  customerName: string;
  customerPhotoUrl?: string;
  location?: string;
  rating: number;
  testimonialText: string;
  relatedServiceId?: string;
  relatedProductId?: string;
  isFeatured: boolean;
  isApproved: boolean;
  displayOrder: number;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}
