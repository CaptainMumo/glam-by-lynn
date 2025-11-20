"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/hooks/useAuth";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { ShoppingCart, MapPin, Plus, Check, AlertCircle, Loader2 } from "lucide-react";
import Image from "next/image";

interface CartItem {
  id: string;
  productId: string;
  productVariantId?: string;
  quantity: number;
  product: {
    id: string;
    title: string;
    slug: string;
    basePrice: number;
    images?: Array<{ url: string; alt_text?: string }>;
  };
}

interface SavedAddress {
  id: string;
  deliveryCounty: string;
  deliveryTown: string;
  deliveryAddress: string;
}

export default function CheckoutPage() {
  const { user, authenticated } = useAuth();
  const router = useRouter();

  // State
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [savedAddresses, setSavedAddresses] = useState<SavedAddress[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Form state
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [addressMode, setAddressMode] = useState<"saved" | "new">("new");
  const [selectedAddressId, setSelectedAddressId] = useState("");
  const [county, setCounty] = useState("");
  const [town, setTown] = useState("");
  const [address, setAddress] = useState("");
  const [promoCode, setPromoCode] = useState("");
  const [promoDiscount, setPromoDiscount] = useState(0);
  const [validatingPromo, setValidatingPromo] = useState(false);

  // Pre-fill user info
  useEffect(() => {
    if (user) {
      setFullName(user.name || "");
      setEmail(user.email || "");
      // Phone is not stored in session, user will need to enter it
    }
  }, [user]);

  // Fetch cart and saved addresses
  useEffect(() => {
    async function fetchData() {
      if (!authenticated) {
        router.push("/auth/signin?redirect=/checkout");
        return;
      }

      try {
        setLoading(true);

        // Fetch cart
        const cartRes = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.GET}`, {
          credentials: "include",
        });

        if (cartRes.ok) {
          const cartData = await cartRes.json();
          setCartItems(cartData.items || []);

          // If cart is empty, redirect to products
          if (!cartData.items || cartData.items.length === 0) {
            router.push("/products");
            return;
          }
        }

        // Fetch saved addresses from previous orders
        const ordersRes = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ORDERS.LIST}?limit=5`, {
          credentials: "include",
        });

        if (ordersRes.ok) {
          const ordersData = await ordersRes.json();
          const addresses: SavedAddress[] = [];
          const seen = new Set<string>();

          for (const order of ordersData.items || []) {
            if (
              order.deliveryCounty &&
              order.deliveryTown &&
              order.deliveryAddress
            ) {
              const key = `${order.deliveryCounty}|${order.deliveryTown}|${order.deliveryAddress}`;
              if (!seen.has(key)) {
                seen.add(key);
                addresses.push({
                  id: order.id,
                  deliveryCounty: order.deliveryCounty,
                  deliveryTown: order.deliveryTown,
                  deliveryAddress: order.deliveryAddress,
                });
              }
            }
          }

          setSavedAddresses(addresses);

          // If we have saved addresses, default to saved mode
          if (addresses.length > 0) {
            setAddressMode("saved");
            setSelectedAddressId(addresses[0].id);
          }
        }
      } catch (err) {
        console.error("Error fetching data:", err);
        setError("Failed to load checkout data");
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [authenticated, router]);

  const validatePromoCode = async () => {
    if (!promoCode.trim()) return;

    setValidatingPromo(true);
    try {
      const subtotal = cartItems.reduce(
        (sum, item) => sum + item.product.basePrice * item.quantity,
        0
      );

      const res = await fetch(
        `${API_BASE_URL}${API_ENDPOINTS.PROMO_CODES.VALIDATE}?code=${encodeURIComponent(
          promoCode
        )}&orderAmount=${subtotal}`,
        { credentials: "include" }
      );

      if (res.ok) {
        const data = await res.json();
        setPromoDiscount(data.discountAmount || 0);
      } else {
        setPromoDiscount(0);
        const errorData = await res.json();
        setError(errorData.detail || "Invalid promo code");
        setTimeout(() => setError(""), 3000);
      }
    } catch (err) {
      console.error("Error validating promo code:", err);
      setPromoDiscount(0);
    } finally {
      setValidatingPromo(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!fullName.trim() || !email.trim() || !phone.trim()) {
      setError("Please fill in all contact information");
      return;
    }

    let finalCounty = county;
    let finalTown = town;
    let finalAddress = address;

    if (addressMode === "saved" && selectedAddressId) {
      const savedAddr = savedAddresses.find((a) => a.id === selectedAddressId);
      if (savedAddr) {
        finalCounty = savedAddr.deliveryCounty;
        finalTown = savedAddr.deliveryTown;
        finalAddress = savedAddr.deliveryAddress;
      }
    }

    if (!finalCounty.trim() || !finalTown.trim() || !finalAddress.trim()) {
      setError("Please provide a complete delivery address");
      return;
    }

    setSubmitting(true);

    try {
      const subtotal = cartItems.reduce(
        (sum, item) => sum + item.product.basePrice * item.quantity,
        0
      );

      const orderData = {
        guestName: fullName,
        guestEmail: email,
        guestPhone: phone,
        deliveryCounty: finalCounty,
        deliveryTown: finalTown,
        deliveryAddress: finalAddress,
        promoCode: promoCode || undefined,
        items: cartItems.map((item) => ({
          productId: item.productId,
          productVariantId: item.productVariantId || undefined,
          quantity: item.quantity,
        })),
      };

      const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.ORDERS.CREATE}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(orderData),
      });

      if (res.ok) {
        const order = await res.json();
        setSuccess(true);

        // Clear cart
        await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.CLEAR}`, {
          method: "DELETE",
          credentials: "include",
        });

        // Redirect to order confirmation
        setTimeout(() => {
          router.push(`/orders/${order.id}`);
        }, 1500);
      } else {
        const errorData = await res.json();
        setError(errorData.detail || "Failed to create order");
      }
    } catch (err) {
      console.error("Error creating order:", err);
      setError("An error occurred while creating your order");
    } finally {
      setSubmitting(false);
    }
  };

  const subtotal = cartItems.reduce(
    (sum, item) => sum + item.product.basePrice * item.quantity,
    0
  );
  const deliveryFee = 200; // Fixed for now
  const discount = promoDiscount;
  const total = subtotal + deliveryFee - discount;

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
          <h1 className="text-3xl font-bold">Checkout</h1>
          <p className="text-muted-foreground">Complete your order</p>
        </div>

        {error && (
          <div className="mb-6 flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-red-800">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div className="mb-6 flex items-center gap-2 rounded-md border border-green-200 bg-green-50 px-4 py-3 text-green-800">
            <Check className="h-5 w-5" />
            <span>Order created successfully! Redirecting...</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="grid gap-8 lg:grid-cols-3">
            {/* Main content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Contact Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Contact Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      required
                      placeholder="+254..."
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Delivery Address */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5" />
                    Delivery Address
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {savedAddresses.length > 0 && (
                    <RadioGroup
                      value={addressMode}
                      onValueChange={(value) => setAddressMode(value as "saved" | "new")}
                    >
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="saved" id="saved" />
                        <Label htmlFor="saved" className="cursor-pointer">
                          Use saved address
                        </Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <RadioGroupItem value="new" id="new" />
                        <Label htmlFor="new" className="cursor-pointer">
                          <Plus className="mr-1 inline h-4 w-4" />
                          Add new address
                        </Label>
                      </div>
                    </RadioGroup>
                  )}

                  {addressMode === "saved" && savedAddresses.length > 0 && (
                    <div className="space-y-2">
                      <Label>Select Address</Label>
                      <RadioGroup
                        value={selectedAddressId}
                        onValueChange={setSelectedAddressId}
                      >
                        {savedAddresses.map((addr) => (
                          <div
                            key={addr.id}
                            className="flex items-start space-x-2 rounded-md border p-4 hover:bg-muted/50"
                          >
                            <RadioGroupItem value={addr.id} id={addr.id} />
                            <Label htmlFor={addr.id} className="flex-1 cursor-pointer">
                              <div className="font-medium">{addr.deliveryTown}</div>
                              <div className="text-sm text-muted-foreground">
                                {addr.deliveryAddress}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {addr.deliveryCounty}
                              </div>
                            </Label>
                          </div>
                        ))}
                      </RadioGroup>
                    </div>
                  )}

                  {addressMode === "new" && (
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="county">County</Label>
                        <Input
                          id="county"
                          value={county}
                          onChange={(e) => setCounty(e.target.value)}
                          required={addressMode === "new"}
                          placeholder="e.g., Nairobi"
                        />
                      </div>
                      <div>
                        <Label htmlFor="town">Town/City</Label>
                        <Input
                          id="town"
                          value={town}
                          onChange={(e) => setTown(e.target.value)}
                          required={addressMode === "new"}
                          placeholder="e.g., Westlands"
                        />
                      </div>
                      <div>
                        <Label htmlFor="address">Street Address</Label>
                        <Textarea
                          id="address"
                          value={address}
                          onChange={(e) => setAddress(e.target.value)}
                          required={addressMode === "new"}
                          placeholder="Building name, street, apartment number..."
                          rows={3}
                        />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Promo Code */}
              <Card>
                <CardHeader>
                  <CardTitle>Promo Code</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter promo code"
                      value={promoCode}
                      onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={validatePromoCode}
                      disabled={validatingPromo || !promoCode.trim()}
                    >
                      {validatingPromo ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        "Apply"
                      )}
                    </Button>
                  </div>
                  {promoDiscount > 0 && (
                    <div className="mt-2 text-sm text-green-600">
                      Promo code applied! You saved KSh {promoDiscount.toFixed(2)}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Order Summary Sidebar */}
            <div className="lg:col-span-1">
              <Card className="sticky top-4">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ShoppingCart className="h-5 w-5" />
                    Order Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Cart Items */}
                  <div className="space-y-3">
                    {cartItems.map((item) => (
                      <div key={item.id} className="flex gap-3">
                        <div className="relative h-16 w-16 flex-shrink-0 overflow-hidden rounded-md bg-muted">
                          {item.product.images?.[0] ? (
                            <Image
                              src={item.product.images[0].url}
                              alt={item.product.title}
                              fill
                              className="object-cover"
                            />
                          ) : (
                            <div className="flex h-full items-center justify-center">
                              <ShoppingCart className="h-6 w-6 text-muted-foreground/50" />
                            </div>
                          )}
                          <Badge
                            variant="secondary"
                            className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs"
                          >
                            {item.quantity}
                          </Badge>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="truncate text-sm font-medium">
                            {item.product.title}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            KSh {item.product.basePrice.toFixed(2)} × {item.quantity}
                          </p>
                        </div>
                        <div className="text-sm font-medium">
                          KSh {(item.product.basePrice * item.quantity).toFixed(2)}
                        </div>
                      </div>
                    ))}
                  </div>

                  <Separator />

                  {/* Totals */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Subtotal</span>
                      <span>KSh {subtotal.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Delivery Fee</span>
                      <span>KSh {deliveryFee.toFixed(2)}</span>
                    </div>
                    {discount > 0 && (
                      <div className="flex justify-between text-sm text-green-600">
                        <span>Discount</span>
                        <span>-KSh {discount.toFixed(2)}</span>
                      </div>
                    )}
                    <Separator />
                    <div className="flex justify-between text-base font-bold">
                      <span>Total</span>
                      <span>KSh {total.toFixed(2)}</span>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    className="w-full"
                    size="lg"
                    disabled={submitting || success}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : success ? (
                      <>
                        <Check className="mr-2 h-4 w-4" />
                        Order Created
                      </>
                    ) : (
                      "Place Order"
                    )}
                  </Button>

                  <p className="text-xs text-center text-muted-foreground">
                    You'll be redirected to your order confirmation
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </form>
      </main>

      <Footer />
    </div>
  );
}
