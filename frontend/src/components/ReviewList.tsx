/**
 * ReviewList Component
 * Displays paginated list of reviews with sorting and filtering
 */

"use client";

import { useState, useEffect } from "react";
import { ReviewItem } from "@/components/ReviewItem";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";
import { getProductReviews, markReviewHelpful, type ReviewListResponse } from "@/lib/reviews";
import type { Review } from "@/types";

interface ReviewListProps {
  productId: string;
  filterRating?: number | null;
}

type SortOption = "newest" | "oldest" | "highest" | "lowest";

export function ReviewList({ productId, filterRating }: ReviewListProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [markingHelpful, setMarkingHelpful] = useState<string | null>(null);

  const pageSize = 10;

  // Fetch reviews
  useEffect(() => {
    const fetchReviews = async () => {
      setLoading(true);
      setError(null);

      try {
        const data: ReviewListResponse = await getProductReviews(productId, page, pageSize);

        let sortedReviews = [...data.reviews];

        // Apply sorting
        switch (sortBy) {
          case "newest":
            sortedReviews.sort(
              (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
            );
            break;
          case "oldest":
            sortedReviews.sort(
              (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
            );
            break;
          case "highest":
            sortedReviews.sort((a, b) => b.rating - a.rating);
            break;
          case "lowest":
            sortedReviews.sort((a, b) => a.rating - b.rating);
            break;
        }

        // Apply rating filter
        if (filterRating) {
          sortedReviews = sortedReviews.filter((review) => review.rating === filterRating);
        }

        setReviews(sortedReviews);
        setTotal(filterRating ? sortedReviews.length : data.total);
        setTotalPages(data.totalPages);
      } catch (err) {
        console.error("Error fetching reviews:", err);
        setError("Failed to load reviews. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [productId, page, sortBy, filterRating]);

  // Reset to page 1 when filter or sort changes
  useEffect(() => {
    setPage(1);
  }, [sortBy, filterRating]);

  const handleMarkHelpful = async (reviewId: string) => {
    setMarkingHelpful(reviewId);

    try {
      await markReviewHelpful(reviewId);

      // Update local state to increment count
      setReviews((prev) =>
        prev.map((review) =>
          review.id === reviewId
            ? { ...review, helpfulCount: review.helpfulCount + 1 }
            : review
        )
      );
    } catch (error) {
      console.error("Error marking review as helpful:", error);
    } finally {
      setMarkingHelpful(null);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="border rounded-lg p-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-4 w-24" />
              </div>
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  // No reviews state
  if (reviews.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">
          {filterRating
            ? `No ${filterRating}-star reviews yet.`
            : "No reviews yet. Be the first to review this product!"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls: Sort */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {reviews.length} of {total} {total === 1 ? "review" : "reviews"}
          {filterRating && ` (${filterRating} stars)`}
        </p>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Sort by:</span>
          <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest</SelectItem>
              <SelectItem value="oldest">Oldest</SelectItem>
              <SelectItem value="highest">Highest Rated</SelectItem>
              <SelectItem value="lowest">Lowest Rated</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Review List */}
      <div className="space-y-4">
        {reviews.map((review) => (
          <ReviewItem
            key={review.id}
            review={review}
            onMarkHelpful={handleMarkHelpful}
            isMarkingHelpful={markingHelpful === review.id}
          />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Previous
          </Button>

          <div className="flex items-center gap-1">
            {[...Array(Math.min(totalPages, 5))].map((_, i) => {
              const pageNum = i + 1;
              return (
                <Button
                  key={pageNum}
                  variant={page === pageNum ? "default" : "outline"}
                  size="sm"
                  onClick={() => setPage(pageNum)}
                >
                  {pageNum}
                </Button>
              );
            })}
            {totalPages > 5 && (
              <>
                <span className="px-2 text-sm text-muted-foreground">...</span>
                <Button
                  variant={page === totalPages ? "default" : "outline"}
                  size="sm"
                  onClick={() => setPage(totalPages)}
                >
                  {totalPages}
                </Button>
              </>
            )}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}
