"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  ShoppingCart,
  Minus,
  Plus,
  X,
  Loader2,
  ArrowRight,
  ShoppingBag,
  Trash2,
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";

interface CartItem {
  id: string;
  cartId: string;
  productId: string;
  productVariantId?: string;
  quantity: number;
  product: {
    id: string;
    title: string;
    slug: string;
    basePrice: number;
    images?: Array<{ imageUrl: string; altText?: string }>;
    inventoryCount: number;
  };
  productVariant?: {
    id: string;
    variantType: string;
    variantValue: string;
    priceAdjustment: number;
  };
}

export default function CartPage() {
  const { authenticated } = useAuth();
  const router = useRouter();

  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingItems, setUpdatingItems] = useState<Set<string>>(new Set());
  const [removingItems, setRemovingItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    if (!authenticated) {
      router.push("/auth/signin?redirect=/cart");
      return;
    }

    fetchCart();
  }, [authenticated, router]);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.GET}`, {
        credentials: "include",
      });

      if (res.ok) {
        const data = await res.json();
        setCartItems(data.items || []);
      }
    } catch (error) {
      console.error("Error fetching cart:", error);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;

    setUpdatingItems((prev) => new Set(prev).add(itemId));

    try {
      const res = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.CART.UPDATE_ITEM(itemId)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({ quantity: newQuantity }),
        }
      );

      if (res.ok) {
        await fetchCart();
      } else {
        const errorData = await res.json();
        alert(errorData.detail || "Failed to update quantity");
      }
    } catch (error) {
      console.error("Error updating quantity:", error);
      alert("Failed to update quantity");
    } finally {
      setUpdatingItems((prev) => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const removeItem = async (itemId: string) => {
    setRemovingItems((prev) => new Set(prev).add(itemId));

    try {
      const res = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.CART.REMOVE_ITEM(itemId)}`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );

      if (res.ok) {
        await fetchCart();
      } else {
        const errorData = await res.json();
        alert(errorData.detail || "Failed to remove item");
      }
    } catch (error) {
      console.error("Error removing item:", error);
      alert("Failed to remove item");
    } finally {
      setRemovingItems((prev) => {
        const newSet = new Set(prev);
        newSet.delete(itemId);
        return newSet;
      });
    }
  };

  const clearCart = async () => {
    if (!confirm("Are you sure you want to clear your cart?")) return;

    try {
      const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.CLEAR}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (res.ok) {
        setCartItems([]);
      } else {
        alert("Failed to clear cart");
      }
    } catch (error) {
      console.error("Error clearing cart:", error);
      alert("Failed to clear cart");
    }
  };

  const getItemPrice = (item: CartItem): number => {
    const basePrice = item.product.basePrice;
    const variantAdjustment = item.productVariant?.priceAdjustment || 0;
    return basePrice + variantAdjustment;
  };

  const getItemTotal = (item: CartItem): number => {
    return getItemPrice(item) * item.quantity;
  };

  const subtotal = cartItems.reduce((sum, item) => sum + getItemTotal(item), 0);

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
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Shopping Cart</h1>
            <p className="text-muted-foreground">
              {cartItems.length} {cartItems.length === 1 ? "item" : "items"} in your
              cart
            </p>
          </div>
          {cartItems.length > 0 && (
            <Button variant="outline" onClick={clearCart}>
              <Trash2 className="mr-2 h-4 w-4" />
              Clear Cart
            </Button>
          )}
        </div>

        {cartItems.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-16">
              <ShoppingCart className="mb-4 h-16 w-16 text-muted-foreground/50" />
              <h2 className="mb-2 text-xl font-semibold">Your cart is empty</h2>
              <p className="mb-6 text-muted-foreground">
                Add some products to get started!
              </p>
              <Button asChild>
                <Link href="/products">
                  <ShoppingBag className="mr-2 h-4 w-4" />
                  Browse Products
                </Link>
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Cart Items */}
            <div className="lg:col-span-2 space-y-4">
              {cartItems.map((item) => (
                <Card key={item.id}>
                  <CardContent className="p-6">
                    <div className="flex gap-4">
                      {/* Product Image */}
                      <Link
                        href={`/products/${item.product.id}`}
                        className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-md border border-border bg-muted"
                      >
                        {item.product.images && item.product.images[0] ? (
                          <Image
                            src={item.product.images[0].imageUrl}
                            alt={item.product.title}
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center">
                            <ShoppingCart className="h-8 w-8 text-muted-foreground/30" />
                          </div>
                        )}
                      </Link>

                      {/* Product Info */}
                      <div className="flex flex-1 flex-col">
                        <div className="flex justify-between">
                          <div className="flex-1">
                            <Link
                              href={`/products/${item.product.id}`}
                              className="font-medium hover:text-secondary"
                            >
                              {item.product.title}
                            </Link>
                            {item.productVariant && (
                              <p className="text-sm text-muted-foreground">
                                {item.productVariant.variantType}:{" "}
                                {item.productVariant.variantValue}
                              </p>
                            )}
                            <p className="mt-1 text-sm font-medium">
                              KSh {getItemPrice(item).toLocaleString()}
                            </p>
                          </div>

                          {/* Remove Button */}
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => removeItem(item.id)}
                            disabled={removingItems.has(item.id)}
                          >
                            {removingItems.has(item.id) ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <X className="h-4 w-4" />
                            )}
                          </Button>
                        </div>

                        <div className="mt-4 flex items-center justify-between">
                          {/* Quantity Controls */}
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() =>
                                updateQuantity(item.id, item.quantity - 1)
                              }
                              disabled={
                                item.quantity <= 1 || updatingItems.has(item.id)
                              }
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <Input
                              type="number"
                              min="1"
                              max={item.product.inventoryCount}
                              value={item.quantity}
                              onChange={(e) => {
                                const newQty = parseInt(e.target.value) || 1;
                                if (
                                  newQty >= 1 &&
                                  newQty <= item.product.inventoryCount
                                ) {
                                  updateQuantity(item.id, newQty);
                                }
                              }}
                              className="h-8 w-16 text-center"
                              disabled={updatingItems.has(item.id)}
                            />
                            <Button
                              variant="outline"
                              size="icon"
                              className="h-8 w-8"
                              onClick={() =>
                                updateQuantity(item.id, item.quantity + 1)
                              }
                              disabled={
                                item.quantity >= item.product.inventoryCount ||
                                updatingItems.has(item.id)
                              }
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </div>

                          {/* Item Total */}
                          <div className="text-right">
                            <p className="text-sm text-muted-foreground">Total</p>
                            <p className="text-lg font-semibold">
                              KSh {getItemTotal(item).toLocaleString()}
                            </p>
                          </div>
                        </div>

                        {/* Stock Warning */}
                        {item.quantity > item.product.inventoryCount && (
                          <p className="mt-2 text-sm text-red-600">
                            Only {item.product.inventoryCount} available in stock
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Cart Summary */}
            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle>Order Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">
                        Subtotal ({cartItems.length}{" "}
                        {cartItems.length === 1 ? "item" : "items"})
                      </span>
                      <span className="font-medium">
                        KSh {subtotal.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Shipping</span>
                      <span className="text-muted-foreground">
                        Calculated at checkout
                      </span>
                    </div>
                  </div>

                  <Separator />

                  <div className="flex justify-between text-lg font-bold">
                    <span>Total</span>
                    <span>KSh {subtotal.toLocaleString()}</span>
                  </div>

                  <Button asChild size="lg" className="w-full">
                    <Link href="/checkout">
                      Proceed to Checkout
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>

                  <Button asChild variant="outline" size="lg" className="w-full">
                    <Link href="/products">Continue Shopping</Link>
                  </Button>

                  <div className="rounded-lg bg-muted p-4 text-sm">
                    <p className="font-medium">Free Shipping</p>
                    <p className="text-muted-foreground">
                      On orders over KSh 5,000
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
