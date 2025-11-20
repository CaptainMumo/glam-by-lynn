"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Heart,
  ShoppingCart,
  Loader2,
  X,
  Star,
  Package,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL } from "@/config/api";

interface WishlistItem {
  id: string;
  userId: string;
  productId: string;
  createdAt: string;
  product: {
    id: string;
    title: string;
    slug: string;
    basePrice: number;
    inventoryCount: number;
    isFeatured: boolean;
    images?: Array<{ imageUrl: string; altText?: string }>;
    brand?: { name: string };
  };
}

export default function WishlistPage() {
  const { authenticated } = useAuth();
  const router = useRouter();

  const [wishlistItems, setWishlistItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [movingToCart, setMovingToCart] = useState<Set<string>>(new Set());
  const [removingItems, setRemovingItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!authenticated) {
      router.push("/auth/signin?redirect=/wishlist");
      return;
    }

    fetchWishlist();
  }, [authenticated, router]);

  const fetchWishlist = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/wishlist`, {
        credentials: "include",
      });

      if (res.ok) {
        const data = await res.json();
        setWishlistItems(data);
      }
    } catch (error) {
      console.error("Error fetching wishlist:", error);
    } finally {
      setLoading(false);
    }
  };

  const moveToCart = async (item: WishlistItem) => {
    setMovingToCart((prev) => new Set(prev).add(item.product.id));

    try {
      // Add to cart
      const cartRes = await fetch(`${API_BASE_URL}/cart/items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          productId: item.product.id,
          quantity: 1,
        }),
      });

      if (cartRes.ok) {
        // Remove from wishlist
        await removeFromWishlist(item.product.id, false);
      } else {
        const errorData = await cartRes.json();
        alert(errorData.detail || "Failed to add to cart");
      }
    } catch (error) {
      console.error("Error moving to cart:", error);
      alert("Failed to move to cart");
    } finally {
      setMovingToCart((prev) => {
        const newSet = new Set(prev);
        newSet.delete(item.product.id);
        return newSet;
      });
    }
  };

  const removeFromWishlist = async (productId: string, showLoading = true) => {
    if (showLoading) {
      setRemovingItems((prev) => new Set(prev).add(productId));
    }

    try {
      const res = await fetch(`${API_BASE_URL}/wishlist/${productId}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (res.ok) {
        await fetchWishlist();
      } else {
        if (showLoading) {
          alert("Failed to remove from wishlist");
        }
      }
    } catch (error) {
      console.error("Error removing from wishlist:", error);
      if (showLoading) {
        alert("Failed to remove from wishlist");
      }
    } finally {
      if (showLoading) {
        setRemovingItems((prev) => {
          const newSet = new Set(prev);
          newSet.delete(productId);
          return newSet;
        });
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <div className="container mx-auto px-4 py-20">
          <div className="flex items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-secondary" />
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">My Wishlist</h1>
          <p className="text-muted-foreground">
            {wishlistItems.length} {wishlistItems.length === 1 ? "item" : "items"} saved
          </p>
        </div>

        {wishlistItems.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <Heart className="mb-4 h-16 w-16 text-muted-foreground/50" />
              <h2 className="mb-2 text-xl font-semibold">Your wishlist is empty</h2>
              <p className="mb-6 text-center text-muted-foreground">
                Save your favorite products to buy them later!
              </p>
              <Button asChild>
                <Link href="/products">
                  <Package className="mr-2 h-4 w-4" />
                  Browse Products
                </Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {wishlistItems.map((item) => (
              <Card
                key={item.id}
                className="group overflow-hidden transition-all hover:shadow-lg"
              >
                {/* Product Image */}
                <Link href={`/products/${item.product.id}`}>
                  <div className="relative aspect-square overflow-hidden bg-muted">
                    {item.product.images && item.product.images[0] ? (
                      <Image
                        src={item.product.images[0].imageUrl}
                        alt={item.product.title}
                        fill
                        className="object-cover transition-transform group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center">
                        <Package className="h-12 w-12 text-muted-foreground/30" />
                      </div>
                    )}
                    {item.product.isFeatured && (
                      <Badge className="absolute left-2 top-2">Featured</Badge>
                    )}
                    <Button
                      variant="secondary"
                      size="icon"
                      className="absolute right-2 top-2"
                      onClick={(e) => {
                        e.preventDefault();
                        removeFromWishlist(item.product.id);
                      }}
                      disabled={removingItems.has(item.product.id)}
                    >
                      {removingItems.has(item.product.id) ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <X className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </Link>

                <CardHeader>
                  <CardTitle className="line-clamp-2 text-base">
                    <Link
                      href={`/products/${item.product.id}`}
                      className="hover:text-secondary"
                    >
                      {item.product.title}
                    </Link>
                  </CardTitle>
                  {item.product.brand && (
                    <p className="text-sm text-muted-foreground">
                      {item.product.brand.name}
                    </p>
                  )}
                </CardHeader>

                <CardContent>
                  <div className="flex items-center justify-between">
                    <span className="text-xl font-bold">
                      KSh {item.product.basePrice.toLocaleString()}
                    </span>
                    {item.product.inventoryCount > 0 ? (
                      <Badge variant="outline" className="border-green-500 text-green-700">
                        In Stock
                      </Badge>
                    ) : (
                      <Badge variant="destructive">Out of Stock</Badge>
                    )}
                  </div>
                </CardContent>

                <CardFooter className="flex gap-2">
                  <Button
                    className="flex-1"
                    onClick={() => moveToCart(item)}
                    disabled={
                      item.product.inventoryCount === 0 ||
                      movingToCart.has(item.product.id)
                    }
                  >
                    {movingToCart.has(item.product.id) ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <ShoppingCart className="mr-2 h-4 w-4" />
                        Add to Cart
                      </>
                    )}
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
