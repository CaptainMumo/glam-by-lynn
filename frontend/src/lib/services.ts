/**
 * Services API client
 * Functions to interact with the booking and services backend API
 */

import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { ServicePackage, PaginatedResponse } from "@/types";

/**
 * Fetch all active service packages
 */
export async function getActiveServicePackages(): Promise<ServicePackage[]> {
  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.SERVICES.LIST}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", // Always fetch fresh data
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch service packages: ${response.statusText}`);
  }

  const data: PaginatedResponse<ServicePackage> = await response.json();
  return data.items;
}

/**
 * Fetch a single service package by ID
 */
export async function getServicePackageById(id: string): Promise<ServicePackage> {
  const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.SERVICES.DETAIL(id)}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch service package: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Format price for display
 */
export function formatPrice(price?: number | string): string {
  if (!price) return "Contact for pricing";
  const numPrice = typeof price === 'string' ? parseFloat(price) : price;
  if (isNaN(numPrice)) return "Contact for pricing";
  return `KSh ${numPrice.toLocaleString()}`;
}

/**
 * Get package type display name
 */
export function getPackageTypeName(packageType: string): string {
  const typeNames: Record<string, string> = {
    bridal_large: "Large Bridal Package",
    bridal_small: "Small Bridal Package",
    bride_only: "Bride Only",
    regular: "Regular Makeup",
    classes: "Makeup Classes",
  };
  return typeNames[packageType] || packageType;
}

/**
 * Get pricing description based on package type
 */
export function getPricingDescription(pkg: ServicePackage): string {
  const prices = [];

  if (pkg.base_bride_price) {
    prices.push(`Bride: ${formatPrice(pkg.base_bride_price)}`);
  }
  if (pkg.base_maid_price) {
    prices.push(`Maid: ${formatPrice(pkg.base_maid_price)}`);
  }
  if (pkg.base_mother_price) {
    prices.push(`Mother: ${formatPrice(pkg.base_mother_price)}`);
  }
  if (pkg.base_other_price) {
    prices.push(`Other: ${formatPrice(pkg.base_other_price)}`);
  }

  if (prices.length === 0) {
    return "Contact for pricing";
  }

  return prices.join(" • ");
}

/**
 * Get package features based on package data
 */
export function getPackageFeatures(pkg: ServicePackage): string[] {
  const features = [];

  // Duration
  if (pkg.duration_minutes) {
    const hours = Math.floor(pkg.duration_minutes / 60);
    const minutes = pkg.duration_minutes % 60;
    if (hours > 0 && minutes > 0) {
      features.push(`${hours}h ${minutes}min session`);
    } else if (hours > 0) {
      features.push(`${hours} hour session`);
    } else {
      features.push(`${minutes} minute session`);
    }
  }

  // Facial inclusion
  if (pkg.includes_facial) {
    features.push("Professional facial included");
  }

  // Group size limits
  if (pkg.min_maids && pkg.max_maids) {
    features.push(`${pkg.min_maids}-${pkg.max_maids} maids/bridesmaids`);
  } else if (pkg.max_maids) {
    features.push(`Up to ${pkg.max_maids} maids/bridesmaids`);
  }

  // Package-specific features
  if (pkg.package_type === "bridal_large" || pkg.package_type === "bridal_small") {
    features.push("Perfect for weddings");
    features.push("Long-lasting makeup formula");
    features.push("Touch-up kit included");
  }

  if (pkg.package_type === "bride_only") {
    features.push("Personalized bridal consultation");
    features.push("Trial session available");
  }

  if (pkg.package_type === "regular") {
    features.push("Suitable for any occasion");
    features.push("Professional makeup application");
  }

  if (pkg.package_type === "classes") {
    features.push("Hands-on training");
    features.push("Product recommendations");
    features.push("Certificate of completion");
  }

  // On-location service (all packages)
  features.push("On-location service available");

  return features;
}
