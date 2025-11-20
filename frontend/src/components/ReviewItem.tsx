/**
 * ReviewItem Component
 * Displays a single product review
 */

"use client";

import { StarRating } from "@/components/StarRating";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ThumbsUp, CheckCircle } from "lucide-react";
import type { Review } from "@/types";

interface ReviewItemProps {
  review: Review;
  onMarkHelpful?: (reviewId: string) => void;
  isMarkingHelpful?: boolean;
}

export function ReviewItem({ review, onMarkHelpful, isMarkingHelpful }: ReviewItemProps) {
  const formattedDate = new Date(review.createdAt).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Header: User info and rating */}
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <p className="font-semibold">
                  {review.user?.fullName || "Anonymous User"}
                </p>
                {review.isVerifiedPurchase && (
                  <Badge variant="secondary" className="flex items-center gap-1 text-xs">
                    <CheckCircle className="h-3 w-3" />
                    Verified Purchase
                  </Badge>
                )}
              </div>
              <p className="text-sm text-muted-foreground">{formattedDate}</p>
            </div>
            <StarRating rating={review.rating} size="sm" />
          </div>

          {/* Review Text */}
          {review.reviewText && (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {review.reviewText}
            </p>
          )}

          {/* Admin Reply */}
          {review.adminReply && (
            <div className="border-l-4 border-secondary bg-muted/30 p-4 rounded-r-md">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="text-xs">
                  Response from Glam by Lynn
                </Badge>
                {review.adminReplyAt && (
                  <span className="text-xs text-muted-foreground">
                    {new Date(review.adminReplyAt).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "short",
                      day: "numeric",
                    })}
                  </span>
                )}
              </div>
              <p className="text-sm leading-relaxed">{review.adminReply}</p>
            </div>
          )}

          {/* Helpful Button */}
          <div className="flex items-center gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onMarkHelpful?.(review.id)}
              disabled={isMarkingHelpful}
              className="gap-2"
            >
              <ThumbsUp className="h-4 w-4" />
              <span>Helpful {review.helpfulCount > 0 && `(${review.helpfulCount})`}</span>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
