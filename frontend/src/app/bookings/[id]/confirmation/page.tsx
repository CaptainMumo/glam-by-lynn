/**
 * Booking Confirmation Page
 * Displays booking confirmation details and next steps
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Booking } from "@/types";
import { getBookingById, formatCurrency, formatDate, formatTime } from "@/lib/bookings";
import { useAuth } from "@/hooks/useAuth";
import {
  Loader2,
  CheckCircle,
  Calendar,
  Clock,
  MapPin,
  Users,
  CreditCard,
  Mail,
  Phone,
  AlertCircle,
} from "lucide-react";

export default function BookingConfirmationPage() {
  const router = useRouter();
  const params = useParams();
  const { session } = useAuth();
  const bookingId = params?.id as string;

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadBooking() {
      if (!bookingId) {
        setError("No booking ID provided");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const token = session?.user?.email ? "dummy-token" : undefined;
        const data = await getBookingById(bookingId, token);
        setBooking(data);
      } catch (err: any) {
        console.error("Failed to load booking:", err);
        setError(err.message || "Failed to load booking details");
      } finally {
        setLoading(false);
      }
    }

    loadBooking();
  }, [bookingId, session]);

  if (loading) {
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

  if (error || !booking) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <div className="container mx-auto flex flex-1 items-center justify-center px-4">
          <Card className="w-full max-w-md border-destructive">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                Error Loading Booking
              </CardTitle>
              <CardDescription>{error || "Booking not found"}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => router.push("/services")} className="w-full">
                Back to Services
              </Button>
            </CardContent>
          </Card>
        </div>
        <Footer />
      </div>
    );
  }

  const totalAttendees =
    booking.numBrides + booking.numMaids + booking.numMothers + booking.numOthers;

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Success Banner */}
      <section className="border-b border-border bg-gradient-to-b from-secondary/10 to-background px-4 py-12">
        <div className="container mx-auto max-w-4xl text-center">
          <div className="mb-4 flex justify-center">
            <div className="rounded-full bg-secondary/20 p-4">
              <CheckCircle className="h-12 w-12 text-secondary" />
            </div>
          </div>
          <h1 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            Booking Confirmed!
          </h1>
          <p className="mb-2 text-lg text-muted-foreground">
            Your booking has been successfully created
          </p>
          <div className="flex items-center justify-center gap-2">
            <span className="text-sm text-muted-foreground">Booking Number:</span>
            <Badge variant="secondary" className="text-base font-mono">
              {booking.bookingNumber}
            </Badge>
          </div>
        </div>
      </section>

      <main className="container mx-auto max-w-4xl px-4 py-12">
        <div className="space-y-6">
          {/* Booking Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Booking Details
              </CardTitle>
              <CardDescription>Your appointment information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Date</p>
                  <p className="font-medium">{formatDate(booking.bookingDate)}</p>
                </div>
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Time</p>
                  <p className="flex items-center gap-2 font-medium">
                    <Clock className="h-4 w-4" />
                    {formatTime(booking.bookingTime)}
                  </p>
                </div>
                {booking.location && (
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p className="flex items-center gap-2 font-medium">
                      <MapPin className="h-4 w-4" />
                      {booking.location.location_name}
                    </p>
                  </div>
                )}
                <div className="space-y-1">
                  <p className="text-sm text-muted-foreground">Status</p>
                  <Badge variant={booking.status === "pending" ? "secondary" : "default"}>
                    {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                  </Badge>
                </div>
              </div>

              {booking.package && (
                <div className="border-t border-border pt-4">
                  <p className="mb-2 text-sm text-muted-foreground">Package</p>
                  <p className="text-lg font-semibold">{booking.package.name}</p>
                  {booking.package.description && (
                    <p className="text-sm text-muted-foreground">{booking.package.description}</p>
                  )}
                </div>
              )}

              <div className="border-t border-border pt-4">
                <p className="mb-3 flex items-center gap-2 text-sm text-muted-foreground">
                  <Users className="h-4 w-4" />
                  Attendees ({totalAttendees} total)
                </p>
                <div className="grid gap-2 text-sm md:grid-cols-2">
                  {booking.numBrides > 0 && (
                    <div className="flex justify-between">
                      <span>Brides:</span>
                      <span className="font-medium">{booking.numBrides}</span>
                    </div>
                  )}
                  {booking.numMaids > 0 && (
                    <div className="flex justify-between">
                      <span>Maids/Bridesmaids:</span>
                      <span className="font-medium">{booking.numMaids}</span>
                    </div>
                  )}
                  {booking.numMothers > 0 && (
                    <div className="flex justify-between">
                      <span>Mothers:</span>
                      <span className="font-medium">{booking.numMothers}</span>
                    </div>
                  )}
                  {booking.numOthers > 0 && (
                    <div className="flex justify-between">
                      <span>Others:</span>
                      <span className="font-medium">{booking.numOthers}</span>
                    </div>
                  )}
                </div>
              </div>

              {booking.weddingTheme && (
                <div className="border-t border-border pt-4">
                  <p className="text-sm text-muted-foreground">Wedding/Event Theme</p>
                  <p className="font-medium">{booking.weddingTheme}</p>
                </div>
              )}

              {booking.specialRequests && (
                <div className="border-t border-border pt-4">
                  <p className="text-sm text-muted-foreground">Special Requests</p>
                  <p className="text-sm">{booking.specialRequests}</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Price Summary */}
          <Card className="border-secondary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Price Summary
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal:</span>
                <span>{formatCurrency(booking.subtotal)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Transport Cost:</span>
                <span>{formatCurrency(booking.transportCost)}</span>
              </div>
              <div className="border-t border-border pt-3">
                <div className="flex justify-between font-semibold">
                  <span>Total Amount:</span>
                  <span>{formatCurrency(booking.totalAmount)}</span>
                </div>
              </div>
              {booking.depositAmount && (
                <div className="rounded-lg bg-secondary/10 p-4">
                  <div className="flex justify-between">
                    <span className="font-medium">Deposit Required (50%):</span>
                    <span className="text-lg font-bold text-secondary">
                      {formatCurrency(booking.depositAmount)}
                    </span>
                  </div>
                  {!booking.depositPaid && (
                    <p className="mt-2 text-sm text-muted-foreground">
                      Payment pending - See payment instructions below
                    </p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Payment Instructions */}
          {booking.depositAmount && !booking.depositPaid && (
            <Card>
              <CardHeader>
                <CardTitle>Payment Instructions</CardTitle>
                <CardDescription>Complete your deposit to confirm your booking</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg bg-muted p-4">
                  <h4 className="mb-2 font-semibold">M-Pesa Payment</h4>
                  <ol className="space-y-2 text-sm">
                    <li className="flex gap-2">
                      <span className="font-semibold">1.</span>
                      <span>Go to M-Pesa on your phone</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold">2.</span>
                      <span>Select Lipa Na M-Pesa, then Pay Bill</span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold">3.</span>
                      <span>
                        Enter Business Number: <strong>123456</strong>
                      </span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold">4.</span>
                      <span>
                        Enter Account Number: <strong>{booking.bookingNumber}</strong>
                      </span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold">5.</span>
                      <span>
                        Enter Amount: <strong>{formatCurrency(booking.depositAmount)}</strong>
                      </span>
                    </li>
                    <li className="flex gap-2">
                      <span className="font-semibold">6.</span>
                      <span>Enter your M-Pesa PIN and confirm</span>
                    </li>
                  </ol>
                </div>

                <div className="rounded-lg border border-border p-4">
                  <h4 className="mb-2 font-semibold">Bank Transfer</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Bank:</span>
                      <span className="font-medium">Equity Bank</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Account Name:</span>
                      <span className="font-medium">Glam by Lynn</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Account Number:</span>
                      <span className="font-medium">1234567890</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Reference:</span>
                      <span className="font-medium">{booking.bookingNumber}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-2 rounded-lg bg-blue-50 p-3 text-sm dark:bg-blue-950/20">
                  <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0 text-blue-600 dark:text-blue-400" />
                  <p className="text-blue-900 dark:text-blue-100">
                    After making payment, send confirmation via WhatsApp to{" "}
                    <strong>+254 700 000 000</strong> or email to{" "}
                    <strong>payments@glambylynn.com</strong>
                  </p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Next Steps */}
          <Card>
            <CardHeader>
              <CardTitle>What Happens Next?</CardTitle>
            </CardHeader>
            <CardContent>
              <ol className="space-y-3">
                <li className="flex gap-3">
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold text-secondary-foreground">
                    1
                  </span>
                  <div>
                    <p className="font-medium">Complete Your Deposit Payment</p>
                    <p className="text-sm text-muted-foreground">
                      Pay the required deposit to secure your booking
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold text-secondary-foreground">
                    2
                  </span>
                  <div>
                    <p className="font-medium">We'll Confirm Your Booking</p>
                    <p className="text-sm text-muted-foreground">
                      You'll receive a confirmation email/SMS within 24 hours
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold text-secondary-foreground">
                    3
                  </span>
                  <div>
                    <p className="font-medium">Prepare for Your Appointment</p>
                    <p className="text-sm text-muted-foreground">
                      We'll send you preparation tips and reminders before your date
                    </p>
                  </div>
                </li>
                <li className="flex gap-3">
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-secondary text-sm font-semibold text-secondary-foreground">
                    4
                  </span>
                  <div>
                    <p className="font-medium">Enjoy Your Service</p>
                    <p className="text-sm text-muted-foreground">
                      Our team will arrive at your location ready to make you look stunning
                    </p>
                  </div>
                </li>
              </ol>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
              <CardDescription>Get in touch with us</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center gap-3">
                <Phone className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Phone / WhatsApp</p>
                  <a href="tel:+254700000000" className="font-medium hover:text-secondary">
                    +254 700 000 000
                  </a>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Mail className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <a
                    href="mailto:info@glambylynn.com"
                    className="font-medium hover:text-secondary"
                  >
                    info@glambylynn.com
                  </a>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 sm:flex-row">
            <Button onClick={() => router.push("/services")} variant="outline" className="flex-1">
              Book Another Service
            </Button>
            <Button onClick={() => router.push("/")} className="flex-1">
              Back to Home
            </Button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
