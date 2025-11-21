/**
 * Booking History Page
 * Displays user's booking list with filtering and management options
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
import { Booking } from "@/types";
import {
  getUserBookings,
  cancelBooking,
  formatCurrency,
  formatDate,
  formatTime,
  formatStatus,
  getStatusBadgeVariant,
} from "@/lib/bookings";
import { useAuth, useRequireAuth } from "@/hooks/useAuth";
import {
  Loader2,
  Calendar,
  Clock,
  MapPin,
  DollarSign,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  XCircle,
} from "lucide-react";

export default function BookingHistoryPage() {
  useRequireAuth(); // Redirect to login if not authenticated

  const router = useRouter();
  const { session } = useAuth();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [cancellingId, setCancellingId] = useState<string | null>(null);

  const pageSize = 10;

  useEffect(() => {
    async function loadBookings() {
      if (!session?.user?.email) {
        return;
      }

      try {
        setLoading(true);
        const token = "dummy-token"; // TODO: Get real token from session
        const data = await getUserBookings(token, page, pageSize, statusFilter || undefined);
        setBookings(data.items);
        setTotal(data.total);
        setTotalPages(data.totalPages);
      } catch (err: any) {
        console.error("Failed to load bookings:", err);
        setError(err.message || "Failed to load bookings");
      } finally {
        setLoading(false);
      }
    }

    loadBookings();
  }, [session, page, statusFilter]);

  const handleCancelBooking = async (bookingId: string) => {
    if (!confirm("Are you sure you want to cancel this booking?")) {
      return;
    }

    try {
      setCancellingId(bookingId);
      const token = "dummy-token"; // TODO: Get real token from session
      await cancelBooking(bookingId, token);

      // Refresh bookings list
      const data = await getUserBookings(token, page, pageSize, statusFilter || undefined);
      setBookings(data.items);
      setTotal(data.total);
      setTotalPages(data.totalPages);

      alert("Booking cancelled successfully");
    } catch (err: any) {
      console.error("Failed to cancel booking:", err);
      alert(err.message || "Failed to cancel booking");
    } finally {
      setCancellingId(null);
    }
  };

  const canCancelBooking = (booking: Booking): boolean => {
    // Can only cancel pending, confirmed, or deposit_paid bookings
    if (!["pending", "confirmed", "deposit_paid"].includes(booking.status)) {
      return false;
    }

    // Check if booking is at least 24 hours away
    const bookingDateTime = new Date(`${booking.bookingDate}T${booking.bookingTime}`);
    const hoursUntilBooking = (bookingDateTime.getTime() - new Date().getTime()) / (1000 * 60 * 60);
    return hoursUntilBooking >= 24;
  };

  if (loading && bookings.length === 0) {
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

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-12">
        <div className="container mx-auto max-w-5xl">
          <h1 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">My Bookings</h1>
          <p className="text-muted-foreground">
            View and manage your makeup service appointments
          </p>
        </div>
      </section>

      <main className="container mx-auto max-w-5xl px-4 py-12">
        {/* Filters */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Filter by status:</span>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="confirmed">Confirmed</SelectItem>
                <SelectItem value="deposit_paid">Deposit Paid</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button onClick={() => router.push("/services")}>Book New Service</Button>
        </div>

        {error && (
          <Card className="mb-6 border-destructive">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <p>{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {bookings.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Calendar className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="mb-2 text-lg font-medium">No bookings found</p>
              <p className="mb-6 text-sm text-muted-foreground">
                {statusFilter
                  ? `No bookings with status "${formatStatus(statusFilter)}"`
                  : "You haven't made any bookings yet"}
              </p>
              <Button onClick={() => router.push("/services")}>Browse Services</Button>
            </CardContent>
          </Card>
        ) : (
          <>
            {/* Bookings List */}
            <div className="space-y-4">
              {bookings.map((booking) => (
                <Card key={booking.id} className="hover:border-secondary/50 transition-colors">
                  <CardHeader>
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                      <div>
                        <div className="mb-2 flex items-center gap-2">
                          <CardTitle className="text-xl">
                            {booking.package?.name || "Service Package"}
                          </CardTitle>
                          <Badge variant={getStatusBadgeVariant(booking.status)}>
                            {formatStatus(booking.status)}
                          </Badge>
                        </div>
                        <CardDescription className="font-mono">
                          {booking.bookingNumber}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => router.push(`/bookings/${booking.id}/confirmation`)}
                        >
                          View Details
                        </Button>
                        {canCancelBooking(booking) && (
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleCancelBooking(booking.id)}
                            disabled={cancellingId === booking.id}
                          >
                            {cancellingId === booking.id ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Cancelling
                              </>
                            ) : (
                              <>
                                <XCircle className="mr-2 h-4 w-4" />
                                Cancel
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm text-muted-foreground">Date</p>
                          <p className="font-medium">{formatDate(booking.bookingDate)}</p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm text-muted-foreground">Time</p>
                          <p className="font-medium">{formatTime(booking.bookingTime)}</p>
                        </div>
                      </div>

                      {booking.location && (
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="text-sm text-muted-foreground">Location</p>
                            <p className="font-medium">{booking.location.location_name}</p>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-muted-foreground" />
                        <div>
                          <p className="text-sm text-muted-foreground">Total</p>
                          <p className="font-medium">{formatCurrency(booking.totalAmount)}</p>
                        </div>
                      </div>
                    </div>

                    {booking.depositAmount && !booking.depositPaid && (
                      <div className="mt-4 rounded-lg bg-secondary/10 p-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm">Deposit Payment Pending:</span>
                          <span className="font-semibold text-secondary">
                            {formatCurrency(booking.depositAmount)}
                          </span>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Showing {(page - 1) * pageSize + 1} to{" "}
                  {Math.min(page * pageSize, total)} of {total} bookings
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
