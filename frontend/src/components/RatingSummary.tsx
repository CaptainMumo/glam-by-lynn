/**
 * RatingSummary Component
 * Displays product rating summary with distribution chart
 */

"use client";

import { StarRating } from "@/components/StarRating";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Star } from "lucide-react";
import type { ProductRatingSummary } from "@/lib/reviews";

interface RatingSummaryProps {
  summary: ProductRatingSummary;
  onFilterByRating?: (rating: number | null) => void;
  selectedRating?: number | null;
}

export function RatingSummary({
  summary,
  onFilterByRating,
  selectedRating,
}: RatingSummaryProps) {
  const { totalReviews, averageRating, ratingDistribution } = summary;

  // Calculate percentages for each rating
  const getPercentage = (count: number) => {
    if (totalReviews === 0) return 0;
    return Math.round((count / totalReviews) * 100);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Customer Reviews</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Rating */}
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="text-5xl font-bold mb-2">{averageRating.toFixed(1)}</div>
            <StarRating rating={averageRating} size="md" showValue={false} />
            <p className="text-sm text-muted-foreground mt-2">
              {totalReviews} {totalReviews === 1 ? "review" : "reviews"}
            </p>
          </div>

          {/* Rating Distribution */}
          <div className="flex-1 space-y-2">
            {[5, 4, 3, 2, 1].map((rating) => {
              const count = ratingDistribution[rating as keyof typeof ratingDistribution] || 0;
              const percentage = getPercentage(count);

              return (
                <button
                  key={rating}
                  onClick={() => onFilterByRating?.(selectedRating === rating ? null : rating)}
                  className={`w-full group ${onFilterByRating ? "cursor-pointer" : "cursor-default"}`}
                  disabled={!onFilterByRating}
                >
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1 w-12">
                      <span className="text-sm font-medium">{rating}</span>
                      <Star className="h-3 w-3 fill-yellow-400 stroke-yellow-400" />
                    </div>

                    {/* Progress Bar */}
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          selectedRating === rating
                            ? "bg-secondary"
                            : "bg-yellow-400 group-hover:bg-yellow-500"
                        }`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>

                    <span className="text-sm text-muted-foreground w-12 text-right">
                      {count}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Clear Filter Button */}
        {selectedRating && onFilterByRating && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onFilterByRating(null)}
            className="w-full"
          >
            Clear Filter
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
