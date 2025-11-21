"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import {
  fetchAdminBookings,
  updateBookingDeposit,
  updateBookingStatus,
  cancelAdminBooking,
  exportBookingsCSV,
} from "@/lib/admin-bookings";
import type { Booking } from "@/types";

const STATUS_OPTIONS = [
  { value: "pending", label: "Pending", color: "bg-yellow-100 text-yellow-800" },
  { value: "confirmed", label: "Confirmed", color: "bg-blue-100 text-blue-800" },
  { value: "deposit_paid", label: "Deposit Paid", color: "bg-green-100 text-green-800" },
  { value: "completed", label: "Completed", color: "bg-gray-100 text-gray-800" },
  { value: "cancelled", label: "Cancelled", color: "bg-red-100 text-red-800" },
];

export default function AdminBookingsPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);

  // Filters
  const [statusFilter, setStatusFilter] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);

  // Redirect if not admin
  useEffect(() => {
    if (status === "unauthenticated") {
      router.push("/auth/signin");
    } else if (status === "authenticated" && !session?.user?.isAdmin) {
      router.push("/");
    }
  }, [status, session, router]);

  // Load bookings
  useEffect(() => {
    if (status === "authenticated" && session?.user?.isAdmin) {
      loadBookings();
    }
  }, [status, session, page, statusFilter, startDate, endDate]);

  const loadBookings = async () => {
    if (!session?.accessToken) return;

    setLoading(true);
    setError(null);

    try {
      const data = await fetchAdminBookings(
        {
          page,
          pageSize: 20,
          status: statusFilter || undefined,
          startDate: startDate || undefined,
          endDate: endDate || undefined,
        },
        session.accessToken
      );

      setBookings(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      console.error("Error loading bookings:", err);
      setError(err.response?.data?.detail || "Failed to load bookings");
    } finally {
      setLoading(false);
    }
  };

  const handleDepositToggle = async (booking: Booking) => {
    if (!session?.accessToken) return;

    try {
      await updateBookingDeposit(
        booking.id,
        {
          depositPaid: !booking.depositPaid,
          adminNotes: `Deposit ${!booking.depositPaid ? "marked as paid" : "marked as unpaid"}`,
        },
        session.accessToken
      );
      await loadBookings();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update deposit");
    }
  };

  const handleStatusChange = async (booking: Booking, newStatus: string) => {
    if (!session?.accessToken) return;

    try {
      await updateBookingStatus(
        booking.id,
        {
          status: newStatus as any,
          adminNotes: `Status changed to ${newStatus}`,
        },
        session.accessToken
      );
      await loadBookings();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update status");
    }
  };

  const handleCancelBooking = async (booking: Booking) => {
    if (!session?.accessToken) return;
    if (!confirm(`Cancel booking ${booking.bookingNumber}?`)) return;

    try {
      await cancelAdminBooking(booking.id, "Admin cancelled", session.accessToken);
      await loadBookings();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to cancel booking");
    }
  };

  const handleExportCSV = async () => {
    if (!session?.accessToken) return;

    try {
      const blob = await exportBookingsCSV(
        {
          status: statusFilter || undefined,
          startDate: startDate || undefined,
          endDate: endDate || undefined,
        },
        session.accessToken
      );

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `bookings_${new Date().toISOString().split("T")[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError("Failed to export CSV");
    }
  };

  const getStatusBadge = (statusValue: string) => {
    const statusOption = STATUS_OPTIONS.find((s) => s.value === statusValue);
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusOption?.color || "bg-gray-100"}`}>
        {statusOption?.label || statusValue}
      </span>
    );
  };

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!session?.user?.isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Booking Management</h1>
            <p className="text-muted-foreground mt-1">Manage all customer bookings</p>
          </div>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
            disabled={loading}
          >
            Export CSV
          </button>
        </div>

        {/* Filters */}
        <div className="bg-card p-4 rounded-lg border mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-secondary"
              >
                <option value="">All Statuses</option>
                {STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => {
                  setStartDate(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-secondary"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => {
                  setEndDate(e.target.value);
                  setPage(1);
                }}
                className="w-full p-2 border rounded focus:outline-none focus:ring-2 focus:ring-secondary"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={() => {
                  setStatusFilter("");
                  setStartDate("");
                  setEndDate("");
                  setPage(1);
                }}
                className="w-full px-4 py-2 border rounded hover:bg-accent transition-colors"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-destructive/10 text-destructive rounded-lg border border-destructive">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center py-8 text-muted-foreground">Loading bookings...</div>
        )}

        {!loading && bookings.length === 0 && (
          <div className="text-center py-12 bg-card rounded-lg border">
            <p className="text-muted-foreground">No bookings found</p>
          </div>
        )}

        {!loading && bookings.length > 0 && (
          <>
            <div className="bg-card rounded-lg border overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium">Booking #</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Customer</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Date & Time</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Status</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Deposit</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Total</th>
                      <th className="px-4 py-3 text-left text-sm font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bookings.map((booking) => (
                      <tr key={booking.id} className="border-t hover:bg-accent/5">
                        <td className="px-4 py-3">
                          <button
                            onClick={() => {
                              setSelectedBooking(booking);
                              setShowDetailsModal(true);
                            }}
                            className="text-secondary hover:underline font-medium"
                          >
                            {booking.bookingNumber}
                          </button>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <div className="font-medium">
                              {booking.guestName || `User ${booking.userId}`}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {booking.guestEmail || booking.guestPhone}
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <div>{booking.bookingDate}</div>
                          <div className="text-sm text-muted-foreground">{booking.bookingTime}</div>
                        </td>
                        <td className="px-4 py-3">
                          <select
                            value={booking.status}
                            onChange={(e) => handleStatusChange(booking, e.target.value)}
                            className="px-2 py-1 border rounded text-sm focus:outline-none focus:ring-2 focus:ring-secondary"
                          >
                            {STATUS_OPTIONS.map((option) => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleDepositToggle(booking)}
                            className={`px-3 py-1 rounded-full text-xs font-medium ${
                              booking.depositPaid
                                ? "bg-green-100 text-green-800"
                                : "bg-yellow-100 text-yellow-800"
                            }`}
                          >
                            {booking.depositPaid ? "Paid" : "Unpaid"}
                          </button>
                        </td>
                        <td className="px-4 py-3 font-medium">
                          KES {booking.totalAmount.toLocaleString()}
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => handleCancelBooking(booking)}
                            className="px-3 py-1 bg-red-100 text-red-800 rounded hover:bg-red-200 text-sm"
                            disabled={booking.status === "cancelled"}
                          >
                            Cancel
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Pagination */}
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {bookings.length} of {total} bookings
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-4 py-2 border rounded hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <div className="px-4 py-2">
                  Page {page} of {totalPages}
                </div>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page === totalPages}
                  className="px-4 py-2 border rounded hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}

        {/* Booking Details Modal */}
        {showDetailsModal && selectedBooking && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">Booking Details</h2>
                  <button
                    onClick={() => setShowDetailsModal(false)}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Booking Number</div>
                      <div className="font-medium">{selectedBooking.bookingNumber}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Status</div>
                      <div>{getStatusBadge(selectedBooking.status)}</div>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-2">Customer Information</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Name</div>
                        <div>{selectedBooking.guestName || "N/A"}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Email</div>
                        <div>{selectedBooking.guestEmail || "N/A"}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Phone</div>
                        <div>{selectedBooking.guestPhone || "N/A"}</div>
                      </div>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-2">Booking Details</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Date</div>
                        <div>{selectedBooking.bookingDate}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Time</div>
                        <div>{selectedBooking.bookingTime}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Brides</div>
                        <div>{selectedBooking.numBrides}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Maids</div>
                        <div>{selectedBooking.numMaids}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Mothers</div>
                        <div>{selectedBooking.numMothers}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Others</div>
                        <div>{selectedBooking.numOthers}</div>
                      </div>
                    </div>
                  </div>

                  {selectedBooking.weddingTheme && (
                    <div className="border-t pt-4">
                      <div className="text-sm text-muted-foreground">Wedding Theme</div>
                      <div>{selectedBooking.weddingTheme}</div>
                    </div>
                  )}

                  {selectedBooking.specialRequests && (
                    <div className="border-t pt-4">
                      <div className="text-sm text-muted-foreground">Special Requests</div>
                      <div>{selectedBooking.specialRequests}</div>
                    </div>
                  )}

                  <div className="border-t pt-4">
                    <h3 className="font-semibold mb-2">Pricing</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Subtotal:</span>
                        <span>KES {selectedBooking.subtotal.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Transport:</span>
                        <span>KES {selectedBooking.transportCost.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between font-bold text-lg">
                        <span>Total:</span>
                        <span>KES {selectedBooking.totalAmount.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Deposit (50%):</span>
                        <span className={selectedBooking.depositPaid ? "text-green-600" : ""}>
                          KES {(selectedBooking.depositAmount || 0).toLocaleString()}
                          {selectedBooking.depositPaid && " ✓"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {selectedBooking.adminNotes && (
                    <div className="border-t pt-4">
                      <div className="text-sm text-muted-foreground mb-2">Admin Notes</div>
                      <div className="bg-muted p-3 rounded whitespace-pre-wrap text-sm">
                        {selectedBooking.adminNotes}
                      </div>
                    </div>
                  )}

                  <div className="border-t pt-4 text-sm text-muted-foreground">
                    <div>Created: {new Date(selectedBooking.createdAt).toLocaleString()}</div>
                    <div>Updated: {new Date(selectedBooking.updatedAt).toLocaleString()}</div>
                  </div>
                </div>

                <div className="mt-6 flex gap-3">
                  <button
                    onClick={() => setShowDetailsModal(false)}
                    className="flex-1 px-4 py-2 border rounded hover:bg-accent transition-colors"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
