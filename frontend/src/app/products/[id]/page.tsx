/**
 * Product Detail Page
 * Enhanced with image gallery, zoom, variants, cart, and wishlist
 */

"use client";

import { useEffect, useState } from "react";
import { use } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReviewSubmissionForm } from "@/components/ReviewSubmissionForm";
import { RatingSummary } from "@/components/RatingSummary";
import { ReviewList } from "@/components/ReviewList";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  AlertCircle,
  ArrowLeft,
  ShoppingCart,
  Heart,
  Minus,
  Plus,
  ZoomIn,
  ChevronLeft,
  ChevronRight,
  Check,
  Loader2,
} from "lucide-react";
import { getProductById } from "@/lib/products";
import { getProductRatingSummary, type ProductRatingSummary } from "@/lib/reviews";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import type { Product } from "@/types";

interface ProductDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function ProductDetailPage({ params }: ProductDetailPageProps) {
  const resolvedParams = use(params);
  const router = useRouter();
  const { authenticated } = useAuth();

  const [product, setProduct] = useState<Product | null>(null);
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [ratingSummary, setRatingSummary] = useState<ProductRatingSummary | null>(null);
  const [filterRating, setFilterRating] = useState<number | null>(null);

  // Product interaction states
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [zoomImageOpen, setZoomImageOpen] = useState(false);
  const [selectedVariant, setSelectedVariant] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [addingToCart, setAddingToCart] = useState(false);
  const [addingToWishlist, setAddingToWishlist] = useState(false);
  const [inWishlist, setInWishlist] = useState(false);
  const [cartSuccess, setCartSuccess] = useState(false);
  const [wishlistSuccess, setWishlistSuccess] = useState(false);

  useEffect(() => {
    const fetchProduct = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getProductById(resolvedParams.id);
        setProduct(data);

        // Fetch related products (same category)
        if (data.categoryId) {
          const relatedRes = await fetch(
            `${API_BASE_URL}${API_ENDPOINTS.PRODUCTS.LIST}?category=${data.categoryId}&limit=4`
          );
          if (relatedRes.ok) {
            const relatedData = await relatedRes.json();
            // Filter out current product
            setRelatedProducts(relatedData.filter((p: Product) => p.id !== data.id).slice(0, 3));
          }
        }
      } catch (err) {
        console.error("Error fetching product:", err);
        setError("Failed to load product details. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [resolvedParams.id, refreshKey]);

  // Fetch rating summary
  useEffect(() => {
    const fetchRatingSummary = async () => {
      try {
        const summary = await getProductRatingSummary(resolvedParams.id);
        setRatingSummary(summary);
      } catch (error) {
        console.error("Error fetching rating summary:", error);
        setRatingSummary({
          totalReviews: 0,
          averageRating: 0,
          ratingDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
        });
      }
    };

    fetchRatingSummary();
  }, [resolvedParams.id, refreshKey]);

  // Check if product is in wishlist
  useEffect(() => {
    const checkWishlist = async () => {
      if (!authenticated || !product) return;

      try {
        const res = await fetch(`${API_BASE_URL}/wishlist`, {
          credentials: "include",
        });
        if (res.ok) {
          const wishlist = await res.json();
          setInWishlist(wishlist.some((item: any) => item.productId === product.id));
        }
      } catch (error) {
        console.error("Error checking wishlist:", error);
      }
    };

    checkWishlist();
  }, [authenticated, product]);

  const handleReviewSubmitted = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const handleFilterByRating = (rating: number | null) => {
    setFilterRating(rating);
  };

  const handleAddToCart = async () => {
    if (!authenticated) {
      router.push("/auth/signin?redirect=/products/" + product?.id);
      return;
    }

    setAddingToCart(true);
    try {
      const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.ADD_ITEM}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          productId: product?.id,
          productVariantId: selectedVariant || undefined,
          quantity,
        }),
      });

      if (res.ok) {
        setCartSuccess(true);
        setTimeout(() => setCartSuccess(false), 3000);
      } else {
        const errorData = await res.json();
        alert(errorData.detail || "Failed to add to cart");
      }
    } catch (error) {
      console.error("Error adding to cart:", error);
      alert("Failed to add to cart");
    } finally {
      setAddingToCart(false);
    }
  };

  const handleToggleWishlist = async () => {
    if (!authenticated) {
      router.push("/auth/signin?redirect=/products/" + product?.id);
      return;
    }

    setAddingToWishlist(true);
    try {
      if (inWishlist) {
        // Remove from wishlist
        const res = await fetch(`${API_BASE_URL}/wishlist/${product?.id}`, {
          method: "DELETE",
          credentials: "include",
        });
        if (res.ok) {
          setInWishlist(false);
        }
      } else {
        // Add to wishlist
        const res = await fetch(`${API_BASE_URL}/wishlist`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ productId: product?.id }),
        });
        if (res.ok) {
          setInWishlist(true);
          setWishlistSuccess(true);
          setTimeout(() => setWishlistSuccess(false), 3000);
        }
      }
    } catch (error) {
      console.error("Error toggling wishlist:", error);
    } finally {
      setAddingToWishlist(false);
    }
  };

  const handlePreviousImage = () => {
    if (!product?.images) return;
    setSelectedImageIndex((prev) =>
      prev === 0 ? product.images!.length - 1 : prev - 1
    );
  };

  const handleNextImage = () => {
    if (!product?.images) return;
    setSelectedImageIndex((prev) =>
      prev === product.images!.length - 1 ? 0 : prev + 1
    );
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
  const hasImages = product.images && product.images.length > 0;
  const currentImage = hasImages && product.images ? product.images[selectedImageIndex] : null;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Success Messages */}
        {cartSuccess && (
          <div className="mb-4 flex items-center gap-2 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-green-800">
            <Check className="h-5 w-5" />
            <span>Added to cart successfully!</span>
          </div>
        )}
        {wishlistSuccess && (
          <div className="mb-4 flex items-center gap-2 rounded-md border border-secondary bg-secondary/10 px-4 py-3 text-secondary">
            <Check className="h-5 w-5" />
            <span>Added to wishlist!</span>
          </div>
        )}

        {/* Back Button */}
        <Button variant="ghost" onClick={() => router.back()} className="mb-6">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Products
        </Button>

        <div className="grid gap-8 lg:grid-cols-2">
          {/* Product Images Section */}
          <div className="space-y-4">
            {/* Main Image */}
            <div className="relative overflow-hidden rounded-lg border border-border bg-muted">
              {hasImages ? (
                <>
                  <div className="relative aspect-square">
                    <Image
                      src={currentImage!.imageUrl}
                      alt={currentImage!.altText || product.title}
                      fill
                      className="object-cover"
                      priority
                    />
                  </div>

                  {/* Zoom Button */}
                  <Button
                    variant="secondary"
                    size="icon"
                    className="absolute right-4 top-4"
                    onClick={() => setZoomImageOpen(true)}
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>

                  {/* Image Navigation */}
                  {product.images && product.images.length > 1 && (
                    <>
                      <Button
                        variant="secondary"
                        size="icon"
                        className="absolute left-4 top-1/2 -translate-y-1/2"
                        onClick={handlePreviousImage}
                      >
                        <ChevronLeft className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="secondary"
                        size="icon"
                        className="absolute right-4 top-1/2 -translate-y-1/2"
                        onClick={handleNextImage}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </>
                  )}

                  {/* Image Counter */}
                  {product.images && product.images.length > 1 && (
                    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full bg-black/60 px-3 py-1 text-sm text-white">
                      {selectedImageIndex + 1} / {product.images.length}
                    </div>
                  )}
                </>
              ) : (
                <div className="flex aspect-square items-center justify-center text-muted-foreground">
                  No image available
                </div>
              )}
            </div>

            {/* Thumbnail Gallery */}
            {hasImages && product.images && product.images.length > 1 && (
              <div className="grid grid-cols-4 gap-2">
                {product.images.map((img, index) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImageIndex(index)}
                    className={`relative aspect-square overflow-hidden rounded-md border-2 ${
                      index === selectedImageIndex
                        ? "border-secondary"
                        : "border-border hover:border-secondary/50"
                    }`}
                  >
                    <Image
                      src={img.imageUrl}
                      alt={img.altText || `${product.title} - ${index + 1}`}
                      fill
                      className="object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
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

            {/* Rating */}
            {ratingSummary && ratingSummary.totalReviews > 0 && (
              <div className="flex items-center gap-2">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <span
                      key={i}
                      className={`text-lg ${
                        i < Math.round(ratingSummary.averageRating)
                          ? "text-secondary"
                          : "text-muted"
                      }`}
                    >
                      ★
                    </span>
                  ))}
                </div>
                <span className="text-sm text-muted-foreground">
                  {ratingSummary.averageRating.toFixed(1)} ({ratingSummary.totalReviews}{" "}
                  reviews)
                </span>
              </div>
            )}

            {/* Price */}
            <div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold">
                  KSh {parseFloat(effectivePrice.toString()).toLocaleString()}
                </span>
                {hasDiscount && (
                  <Badge variant="destructive">
                    {product.discountType === "percentage"
                      ? `${product.discountValue}% OFF`
                      : `KSh ${product.discountValue} OFF`}
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

            {/* Variant Selector */}
            {product.variants && product.variants.length > 0 && (
              <div className="space-y-2">
                <Label>Select Variant</Label>
                <Select
                  value={selectedVariant || undefined}
                  onValueChange={setSelectedVariant}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a variant" />
                  </SelectTrigger>
                  <SelectContent>
                    {product.variants.map((variant) => (
                      <SelectItem key={variant.id} value={variant.id}>
                        {variant.variantType}: {variant.variantValue}
                        {variant.priceAdjustment !== 0 && (
                          <span className="ml-2 text-sm text-muted-foreground">
                            (+KSh {variant.priceAdjustment.toLocaleString()})
                          </span>
                        )}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Quantity Selector */}
            <div className="space-y-2">
              <Label>Quantity</Label>
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  disabled={quantity <= 1}
                >
                  <Minus className="h-4 w-4" />
                </Button>
                <Input
                  type="number"
                  min="1"
                  max={product.inventoryCount}
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-20 text-center"
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() =>
                    setQuantity(Math.min(product.inventoryCount, quantity + 1))
                  }
                  disabled={quantity >= product.inventoryCount}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Tags */}
            {product.tags && product.tags.length > 0 && (
              <div>
                <h2 className="mb-2 text-sm font-semibold">Tags</h2>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <Button
                size="lg"
                className="flex-1"
                disabled={product.inventoryCount === 0 || addingToCart}
                onClick={handleAddToCart}
              >
                {addingToCart ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <ShoppingCart className="mr-2 h-5 w-5" />
                    {product.inventoryCount === 0 ? "Out of Stock" : "Add to Cart"}
                  </>
                )}
              </Button>
              <Button
                size="lg"
                variant={inWishlist ? "secondary" : "outline"}
                onClick={handleToggleWishlist}
                disabled={addingToWishlist}
              >
                {addingToWishlist ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Heart
                    className={`h-5 w-5 ${inWishlist ? "fill-current" : ""}`}
                  />
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Related Products */}
        {relatedProducts.length > 0 && (
          <div className="mt-16">
            <h2 className="mb-6 text-2xl font-bold">Related Products</h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {relatedProducts.map((relatedProduct) => (
                <Card
                  key={relatedProduct.id}
                  className="group cursor-pointer overflow-hidden transition-all hover:shadow-lg"
                  onClick={() => router.push(`/products/${relatedProduct.id}`)}
                >
                  <div className="relative aspect-square overflow-hidden bg-muted">
                    {relatedProduct.images && relatedProduct.images[0] ? (
                      <Image
                        src={relatedProduct.images[0].imageUrl}
                        alt={relatedProduct.title}
                        fill
                        className="object-cover transition-transform group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <ShoppingCart className="h-12 w-12 text-muted-foreground/30" />
                      </div>
                    )}
                  </div>
                  <CardHeader>
                    <CardTitle className="line-clamp-2 text-lg">
                      {relatedProduct.title}
                    </CardTitle>
                    {relatedProduct.brand && (
                      <p className="text-sm text-muted-foreground">
                        {relatedProduct.brand.name}
                      </p>
                    )}
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <span className="text-xl font-bold">
                        KSh {relatedProduct.basePrice.toLocaleString()}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Review Submission Form */}
        <div className="mt-16">
          <ReviewSubmissionForm
            productId={product.id}
            productTitle={product.title}
            onReviewSubmitted={handleReviewSubmitted}
          />
        </div>

        {/* Reviews Display Section */}
        {ratingSummary && ratingSummary.totalReviews > 0 && (
          <div className="mt-12 space-y-8">
            <h2 className="text-2xl font-bold">Customer Reviews</h2>

            {/* Rating Summary */}
            <RatingSummary
              summary={ratingSummary}
              onFilterByRating={handleFilterByRating}
              selectedRating={filterRating}
            />

            {/* Review List */}
            <ReviewList productId={product.id} filterRating={filterRating} />
          </div>
        )}
      </main>

      {/* Image Zoom Dialog */}
      <Dialog open={zoomImageOpen} onOpenChange={setZoomImageOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{product.title}</DialogTitle>
          </DialogHeader>
          {currentImage && (
            <div className="relative aspect-square w-full">
              <Image
                src={currentImage.imageUrl}
                alt={currentImage.altText || product.title}
                fill
                className="object-contain"
              />
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
