/**
 * Order History Page
 * Displays user's order list with filtering and management options
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Order } from "@/types";
import {
  getUserOrders,
  formatCurrency,
  formatDate,
  formatStatus,
  getStatusBadgeVariant,
} from "@/lib/orders";
import { useAuth, useRequireAuth } from "@/hooks/useAuth";
import {
  Loader2,
  Package,
  MapPin,
  DollarSign,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Eye,
  ShoppingCart,
} from "lucide-react";

export default function OrderHistoryPage() {
  useRequireAuth(); // Redirect to login if not authenticated

  const router = useRouter();
  const { session } = useAuth();

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const limit = 10;

  useEffect(() => {
    async function loadOrders() {
      if (!session?.user?.email) {
        return;
      }

      try {
        setLoading(true);
        const token = "dummy-token"; // TODO: Get real token from session
        const data = await getUserOrders(token, skip, limit);
        setOrders(data.orders);
        setTotal(data.total);
      } catch (err: any) {
        console.error("Failed to load orders:", err);
        setError(err.message || "Failed to load orders");
      } finally {
        setLoading(false);
      }
    }

    loadOrders();
  }, [session, skip]);

  const handlePageChange = (newSkip: number) => {
    setSkip(newSkip);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  // Filter orders by status on client side (could be moved to backend API)
  const filteredOrders = statusFilter
    ? orders.filter((order) => order.status === statusFilter)
    : orders;

  if (loading && orders.length === 0) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <div className="flex flex-1 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-secondary" />
        </div>
        <Footer />
      </div>
    );
  }

  if (error && orders.length === 0) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <div className="container mx-auto flex flex-1 items-center justify-center px-4">
          <Card className="w-full max-w-md border-destructive">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                Error Loading Orders
              </CardTitle>
              <CardDescription>{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => window.location.reload()} className="w-full">
                Try Again
              </Button>
            </CardContent>
          </Card>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold tracking-tight">My Orders</h1>
          <p className="text-muted-foreground">
            View and track all your product orders
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-muted-foreground" />
              <span className="text-sm font-medium">
                {total} {total === 1 ? "order" : "orders"} total
              </span>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Filter by status:</span>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="payment_confirmed">Payment Confirmed</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Orders List */}
        {filteredOrders.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Package className="mb-4 h-12 w-12 text-muted-foreground" />
              <h3 className="mb-2 text-lg font-semibold">No orders found</h3>
              <p className="mb-6 text-center text-sm text-muted-foreground">
                {statusFilter
                  ? `You don't have any ${formatStatus(statusFilter).toLowerCase()} orders yet.`
                  : "You haven't placed any orders yet. Start shopping!"}
              </p>
              <Button onClick={() => router.push("/products")}>
                <ShoppingCart className="mr-2 h-4 w-4" />
                Browse Products
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredOrders.map((order) => (
              <Card key={order.id} className="hover:border-secondary/50 transition-colors">
                <CardContent className="p-6">
                  <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                    {/* Order Info */}
                    <div className="flex-1 space-y-3">
                      {/* Order Number & Status */}
                      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
                        <div>
                          <p className="text-sm text-muted-foreground">Order Number</p>
                          <p className="font-mono font-semibold">{order.orderNumber}</p>
                        </div>
                        <Badge variant={getStatusBadgeVariant(order.status)}>
                          {formatStatus(order.status)}
                        </Badge>
                        {order.paymentConfirmed && (
                          <Badge variant="outline" className="border-green-500 text-green-600 dark:text-green-400">
                            Paid
                          </Badge>
                        )}
                      </div>

                      {/* Order Date */}
                      <div>
                        <p className="text-sm text-muted-foreground">Order Date</p>
                        <p className="text-sm">{formatDate(order.createdAt)}</p>
                      </div>

                      {/* Delivery Info */}
                      {order.deliveryAddress && (
                        <div className="flex items-start gap-2">
                          <MapPin className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Delivery Address</p>
                            <p className="text-sm">
                              {order.deliveryAddress}, {order.deliveryTown}, {order.deliveryCounty}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Order Items Count */}
                      {order.orderItems && order.orderItems.length > 0 && (
                        <div>
                          <p className="text-sm text-muted-foreground">
                            {order.orderItems.length} {order.orderItems.length === 1 ? "item" : "items"}
                          </p>
                        </div>
                      )}
                    </div>

                    {/* Amount & Actions */}
                    <div className="flex flex-col items-start gap-3 md:items-end">
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground">Total Amount</p>
                        <p className="text-xl font-bold text-secondary">
                          {formatCurrency(order.totalAmount)}
                        </p>
                      </div>

                      <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row">
                        <Button
                          onClick={() => router.push(`/orders/${order.id}/confirmation`)}
                          variant="outline"
                          size="sm"
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && filteredOrders.length > 0 && (
          <div className="mt-8 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Showing {skip + 1} to {Math.min(skip + limit, total)} of {total} orders
            </p>
            <div className="flex gap-2">
              <Button
                onClick={() => handlePageChange(Math.max(0, skip - limit))}
                disabled={skip === 0}
                variant="outline"
                size="sm"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="flex items-center px-4 text-sm">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                onClick={() => handlePageChange(skip + limit)}
                disabled={skip + limit >= total}
                variant="outline"
                size="sm"
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Empty State for New Users */}
        {orders.length === 0 && !loading && (
          <Card className="mt-8">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <ShoppingCart className="mb-4 h-16 w-16 text-muted-foreground" />
              <h3 className="mb-2 text-xl font-semibold">Start Your Beauty Journey</h3>
              <p className="mb-6 max-w-md text-center text-sm text-muted-foreground">
                Discover our curated collection of premium beauty products. From makeup to skincare,
                we have everything you need to look and feel your best.
              </p>
              <Button onClick={() => router.push("/products")} size="lg">
                <ShoppingCart className="mr-2 h-5 w-5" />
                Browse Products
              </Button>
            </CardContent>
          </Card>
        )}
      </main>

      <Footer />
    </div>
  );
}
