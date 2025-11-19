/**
 * Review API utilities
 */

import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { Review } from "@/types";

export interface ReviewCreateData {
  rating: number;
  reviewText?: string;
}

export interface ReviewListResponse {
  reviews: Review[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  averageRating?: number;
}

export interface ProductRatingSummary {
  totalReviews: number;
  averageRating: number;
  ratingDistribution: {
    1: number;
    2: number;
    3: number;
    4: number;
    5: number;
  };
}

/**
 * Create a review for a product
 */
export async function createReview(
  productId: string,
  reviewData: ReviewCreateData,
  token: string
): Promise<Review> {
  const response = await axios.post<Review>(
    `${API_BASE_URL}${API_ENDPOINTS.REVIEWS.CREATE(productId)}`,
    reviewData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Get reviews for a product with pagination
 */
export async function getProductReviews(
  productId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<ReviewListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    pageSize: pageSize.toString(),
  });

  const response = await axios.get<ReviewListResponse>(
    `${API_BASE_URL}${API_ENDPOINTS.REVIEWS.LIST(productId)}?${params.toString()}`
  );

  return response.data;
}

/**
 * Get product rating summary
 */
export async function getProductRatingSummary(
  productId: string
): Promise<ProductRatingSummary> {
  const response = await axios.get<ProductRatingSummary>(
    `${API_BASE_URL}${API_ENDPOINTS.REVIEWS.SUMMARY(productId)}`
  );

  return response.data;
}

/**
 * Update own review
 */
export async function updateReview(
  reviewId: string,
  reviewData: ReviewCreateData,
  token: string
): Promise<Review> {
  const response = await axios.put<Review>(
    `${API_BASE_URL}${API_ENDPOINTS.REVIEWS.UPDATE(reviewId)}`,
    reviewData,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  return response.data;
}

/**
 * Delete own review
 */
export async function deleteReview(reviewId: string, token: string): Promise<void> {
  await axios.delete(`${API_BASE_URL}${API_ENDPOINTS.REVIEWS.DELETE(reviewId)}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
}

/**
 * Mark a review as helpful
 */
export async function markReviewHelpful(reviewId: string): Promise<void> {
  await axios.post(`${API_BASE_URL}${API_ENDPOINTS.REVIEWS.MARK_HELPFUL(reviewId)}`);
}

/**
 * Check if current user has reviewed a product
 */
export async function hasUserReviewedProduct(
  productId: string,
  token: string
): Promise<boolean> {
  try {
    // Get all reviews for the product
    const response = await getProductReviews(productId, 1, 100);

    // This would ideally be a backend endpoint, but for now we check reviews
    // The backend should handle this properly by checking user_id
    return false; // For now, let the backend handle duplicate check
  } catch (error) {
    return false;
  }
}
