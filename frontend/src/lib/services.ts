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
export function formatPrice(price?: number): string {
  if (!price) return "Contact for pricing";
  return `KSh ${price.toLocaleString()}`;
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

  if (pkg.baseBridePrice) {
    prices.push(`Bride: ${formatPrice(pkg.baseBridePrice)}`);
  }
  if (pkg.baseMaidPrice) {
    prices.push(`Maid: ${formatPrice(pkg.baseMaidPrice)}`);
  }
  if (pkg.baseMotherPrice) {
    prices.push(`Mother: ${formatPrice(pkg.baseMotherPrice)}`);
  }
  if (pkg.baseOtherPrice) {
    prices.push(`Other: ${formatPrice(pkg.baseOtherPrice)}`);
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
  if (pkg.durationMinutes) {
    const hours = Math.floor(pkg.durationMinutes / 60);
    const minutes = pkg.durationMinutes % 60;
    if (hours > 0 && minutes > 0) {
      features.push(`${hours}h ${minutes}min session`);
    } else if (hours > 0) {
      features.push(`${hours} hour session`);
    } else {
      features.push(`${minutes} minute session`);
    }
  }

  // Facial inclusion
  if (pkg.includesFacial) {
    features.push("Professional facial included");
  }

  // Group size limits
  if (pkg.minMaids && pkg.maxMaids) {
    features.push(`${pkg.minMaids}-${pkg.maxMaids} maids/bridesmaids`);
  } else if (pkg.maxMaids) {
    features.push(`Up to ${pkg.maxMaids} maids/bridesmaids`);
  }

  // Package-specific features
  if (pkg.packageType === "bridal_large" || pkg.packageType === "bridal_small") {
    features.push("Perfect for weddings");
    features.push("Long-lasting makeup formula");
    features.push("Touch-up kit included");
  }

  if (pkg.packageType === "bride_only") {
    features.push("Personalized bridal consultation");
    features.push("Trial session available");
  }

  if (pkg.packageType === "regular") {
    features.push("Suitable for any occasion");
    features.push("Professional makeup application");
  }

  if (pkg.packageType === "classes") {
    features.push("Hands-on training");
    features.push("Product recommendations");
    features.push("Certificate of completion");
  }

  // On-location service (all packages)
  features.push("On-location service available");

  return features;
}
