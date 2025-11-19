/**
 * Product Detail Page
 * Displays product information and review submission form
 */

"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReviewSubmissionForm } from "@/components/ReviewSubmissionForm";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, ArrowLeft, ShoppingCart } from "lucide-react";
import { getProductById } from "@/lib/products";
import type { Product } from "@/types";

interface ProductDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();

  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getProductById(resolvedParams.id);
        setProduct(data);
      } catch (err) {
        console.error("Error fetching product:", err);
        setError("Failed to load product details. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [resolvedParams.id, refreshKey]);

  const handleReviewSubmitted = () => {
    // Refresh the page to show the updated review status
    setRefreshKey((prev) => prev + 1);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Skeleton className="mb-4 h-10 w-32" />
          <div className="grid gap-8 lg:grid-cols-2">
            <Skeleton className="h-96 w-full" />
            <div className="space-y-4">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Button variant="ghost" onClick={() => router.back()} className="mb-6">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <AlertCircle className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="mb-4 text-lg font-medium">
                {error || "Product not found"}
              </p>
              <Button onClick={() => router.push("/products")}>
                Browse All Products
              </Button>
            </CardContent>
          </Card>
        </main>
        <Footer />
      </div>
    );
  }

  const effectivePrice = product.basePrice;
  const hasDiscount =
    product.discountType && product.discountValue && product.discountValue > 0;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <Button variant="ghost" onClick={() => router.back()} className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Products
        </Button>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Product Image Section */}
          <div className="space-y-4">
            <div className="overflow-hidden rounded-lg border border-border bg-muted">
              {product.images && product.images.length > 0 ? (
                <img
                  src={product.images[0].imageUrl}
                  alt={product.images[0].altText || product.title}
                  className="h-96 w-full object-cover"
                />
              ) : (
                <div className="flex h-96 w-full items-center justify-center text-muted-foreground">
                  No image available
                </div>
              )}
            </div>
            {/* Additional images could be shown here */}
          </div>

          {/* Product Info Section */}
          <div className="space-y-6">
            {/* Title and Brand */}
            <div>
              <div className="mb-2 flex items-center gap-2">
                {product.brand && (
                  <Badge variant="outline">{product.brand.name}</Badge>
                )}
                {product.category && (
                  <Badge variant="secondary">{product.category.name}</Badge>
                )}
                {product.isFeatured && <Badge>Featured</Badge>}
              </div>
              <h1 className="text-3xl font-bold tracking-tight">{product.title}</h1>
              {product.sku && (
                <p className="text-sm text-muted-foreground">SKU: {product.sku}</p>
              )}
            </div>

            {/* Price */}
            <div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">
                  ${parseFloat(effectivePrice.toString()).toFixed(2)}
                </span>
                {hasDiscount && (
                  <Badge variant="destructive">
                    {product.discountType === "percentage"
                      ? `${product.discountValue}% OFF`
                      : `$${product.discountValue} OFF`}
                  </Badge>
                )}
              </div>
            </div>

            {/* Stock Status */}
            <div>
              {product.inventoryCount > 0 ? (
                <Badge variant="outline" className="border-green-500 text-green-700">
                  In Stock ({product.inventoryCount} available)
                </Badge>
              ) : (
                <Badge variant="destructive">Out of Stock</Badge>
              )}
            </div>

            {/* Description */}
            {product.description && (
              <div>
                <h2 className="mb-2 text-lg font-semibold">Description</h2>
                <p className="text-muted-foreground">{product.description}</p>
              </div>
            )}

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div>
                <h2 className="mb-2 text-lg font-semibold">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Add to Cart Button */}
            <Button
              size="lg"
              className="w-full"
              disabled={product.inventoryCount === 0}
            >
              <ShoppingCart className="mr-2 h-5 w-5" />
              {product.inventoryCount === 0 ? "Out of Stock" : "Add to Cart"}
            </Button>
          </div>
        </div>

        {/* Review Submission Form */}
        <div className="mt-12">
          <ReviewSubmissionForm
            productId={product.id}
            productTitle={product.title}
            onReviewSubmitted={handleReviewSubmitted}
          />
        </div>
      </main>

      <Footer />
    </div>
  );
}
