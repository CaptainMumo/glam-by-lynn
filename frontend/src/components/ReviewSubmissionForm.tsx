/**
 * ReviewSubmissionForm Component
 * Allows users to submit product reviews
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import { StarRating } from "@/components/StarRating";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { createReview } from "@/lib/reviews";
import { AlertCircle, CheckCircle2, Loader2 } from "lucide-react";

interface ReviewSubmissionFormProps {
  productId: string;
  productTitle: string;
  userHasReviewed?: boolean;
  onReviewSubmitted?: () => void;
}

export function ReviewSubmissionForm({
  productId,
  productTitle,
  userHasReviewed = false,
  onReviewSubmitted,
}: ReviewSubmissionFormProps) {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [rating, setRating] = useState<number>(5);
  const [reviewText, setReviewText] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });

  // Loading state
  if (status === "loading") {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Write a Review</CardTitle>
          <CardDescription>Loading...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  // User not authenticated
  if (!session) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Write a Review</CardTitle>
          <CardDescription>Share your experience with {productTitle}</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Please sign in to write a review for this product.
            </AlertDescription>
          </Alert>
          <Button onClick={() => router.push("/auth/signin")} className="mt-4 w-full">
            Sign In to Review
          </Button>
        </CardContent>
      </Card>
    );
  }

  // User has already reviewed
  if (userHasReviewed) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Write a Review</CardTitle>
          <CardDescription>Share your experience with {productTitle}</CardDescription>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              You have already submitted a review for this product. You can only review a product once.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate review text
    if (reviewText.trim().length > 0 && reviewText.trim().length < 10) {
      setSubmitStatus({
        type: "error",
        message: "Review text must be at least 10 characters long.",
      });
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus({ type: null, message: "" });

    try {
      // Get access token from session
      const token = session.accessToken as string;

      await createReview(
        productId,
        {
          rating,
          reviewText: reviewText.trim() || undefined,
        },
        token
      );

      setSubmitStatus({
        type: "success",
        message:
          "Thank you for your review! It will be visible after admin approval.",
      });

      // Reset form
      setRating(5);
      setReviewText("");

      // Notify parent component
      if (onReviewSubmitted) {
        onReviewSubmitted();
      }
    } catch (error: any) {
      console.error("Error submitting review:", error);

      let errorMessage = "Failed to submit review. Please try again.";
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      }

      setSubmitStatus({
        type: "error",
        message: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Write a Review</CardTitle>
        <CardDescription>Share your experience with {productTitle}</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Rating Selection */}
          <div className="space-y-2">
            <Label htmlFor="rating" className="text-base font-semibold">
              Your Rating <span className="text-destructive">*</span>
            </Label>
            <div className="flex items-center gap-2">
              <StarRating
                rating={rating}
                interactive
                onChange={setRating}
                size="lg"
              />
              <span className="text-sm text-muted-foreground">
                {rating} {rating === 1 ? "star" : "stars"}
              </span>
            </div>
          </div>

          {/* Review Text */}
          <div className="space-y-2">
            <Label htmlFor="reviewText" className="text-base font-semibold">
              Your Review (optional)
            </Label>
            <Textarea
              id="reviewText"
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
              placeholder="Tell us about your experience with this product... (minimum 10 characters if provided)"
              className="min-h-[120px] resize-none"
              maxLength={5000}
            />
            {reviewText.length > 0 && (
              <p className="text-xs text-muted-foreground">
                {reviewText.length} / 5000 characters
              </p>
            )}
          </div>

          {/* Submit Status Messages */}
          {submitStatus.type === "success" && (
            <Alert className="border-green-500 bg-green-50 text-green-900">
              <CheckCircle2 className="h-4 w-4 text-green-600" />
              <AlertDescription>{submitStatus.message}</AlertDescription>
            </Alert>
          )}

          {submitStatus.type === "error" && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{submitStatus.message}</AlertDescription>
            </Alert>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            disabled={isSubmitting || submitStatus.type === "success"}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Submitting...
              </>
            ) : submitStatus.type === "success" ? (
              <>
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Review Submitted
              </>
            ) : (
              "Submit Review"
            )}
          </Button>

          {submitStatus.type === null && (
            <p className="text-xs text-center text-muted-foreground">
              Your review will be reviewed by our team before being published.
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
