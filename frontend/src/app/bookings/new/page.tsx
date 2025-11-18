/**
 * New Booking Page
 * Form for creating makeup service bookings
 */

"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ServicePackage, TransportLocation } from "@/types";
import { getActiveServicePackages } from "@/lib/services";
import {
  getTransportLocations,
  createBooking,
  calculateBookingPrice,
  formatCurrency,
} from "@/lib/bookings";
import { useAuth } from "@/hooks/useAuth";
import { Loader2, Calendar, MapPin, Users, DollarSign } from "lucide-react";

function BookingFormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, session } = useAuth();

  // State
  const [packages, setPackages] = useState<ServicePackage[]>([]);
  const [locations, setLocations] = useState<TransportLocation[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [selectedPackageId, setSelectedPackageId] = useState<string>("");
  const [selectedLocationId, setSelectedLocationId] = useState<string>("");
  const [bookingDate, setBookingDate] = useState<string>("");
  const [bookingTime, setBookingTime] = useState<string>("");
  const [numBrides, setNumBrides] = useState<number>(1);
  const [numMaids, setNumMaids] = useState<number>(0);
  const [numMothers, setNumMothers] = useState<number>(0);
  const [numOthers, setNumOthers] = useState<number>(0);
  const [weddingTheme, setWeddingTheme] = useState<string>("");
  const [specialRequests, setSpecialRequests] = useState<string>("");

  // Guest info (if not authenticated)
  const [guestName, setGuestName] = useState<string>("");
  const [guestEmail, setGuestEmail] = useState<string>("");
  const [guestPhone, setGuestPhone] = useState<string>("");

  // Derived state
  const selectedPackage = packages.find((p) => p.id === selectedPackageId);
  const selectedLocation = locations.find((l) => l.id === selectedLocationId);

  // Load data
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [packagesData, locationsData] = await Promise.all([
          getActiveServicePackages(),
          getTransportLocations(),
        ]);
        setPackages(packagesData);
        setLocations(locationsData);

        // Pre-select package from URL param
        const packageId = searchParams?.get("packageId");
        if (packageId && packagesData.find((p) => p.id === packageId)) {
          setSelectedPackageId(packageId);
        }
      } catch (err) {
        console.error("Failed to load booking data:", err);
        setError("Failed to load booking form. Please try again later.");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, [searchParams]);

  // Calculate price
  const pricing = selectedPackage && selectedLocation
    ? calculateBookingPrice(
        parseFloat(selectedPackage.base_bride_price || "0"),
        parseFloat(selectedPackage.base_maid_price || "0"),
        parseFloat(selectedPackage.base_mother_price || "0"),
        parseFloat(selectedPackage.base_other_price || "0"),
        numBrides,
        numMaids,
        numMothers,
        numOthers,
        parseFloat(selectedLocation.transport_cost)
      )
    : null;

  // Validation
  const canSubmit =
    selectedPackageId &&
    selectedLocationId &&
    bookingDate &&
    bookingTime &&
    (user || (guestName && guestEmail && guestPhone)) &&
    pricing &&
    pricing.total > 0;

  // Package validation
  const attendeeErrors = [];
  if (selectedPackage) {
    if (selectedPackage.min_maids && numMaids < selectedPackage.min_maids) {
      attendeeErrors.push(`Minimum ${selectedPackage.min_maids} maid(s) required for this package`);
    }
    if (selectedPackage.max_maids && numMaids > selectedPackage.max_maids) {
      attendeeErrors.push(`Maximum ${selectedPackage.max_maids} maid(s) allowed for this package`);
    }
  }

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!canSubmit) {
      setError("Please fill in all required fields");
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      const bookingData = {
        package_id: selectedPackageId,
        booking_date: bookingDate,
        booking_time: bookingTime,
        location_id: selectedLocationId,
        num_brides: numBrides,
        num_maids: numMaids,
        num_mothers: numMothers,
        num_others: numOthers,
        wedding_theme: weddingTheme || undefined,
        special_requests: specialRequests || undefined,
        ...(!user && {
          guest_name: guestName,
          guest_email: guestEmail,
          guest_phone: guestPhone,
        }),
      };

      const token = session?.user?.accessToken; // Get real JWT token from session
      const booking = await createBooking(bookingData, token);

      // Redirect to confirmation page
      router.push(`/bookings/${booking.id}/confirmation`);
    } catch (err: any) {
      console.error("Failed to create booking:", err);
      setError(err.message || "Failed to create booking. Please try again.");
      setSubmitting(false);
    }
  };

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

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-12">
        <div className="container mx-auto max-w-4xl">
          <h1 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            Book Your Service
          </h1>
          <p className="text-muted-foreground">
            Fill out the form below to reserve your makeup appointment
          </p>
        </div>
      </section>

      {/* Booking Form */}
      <main className="container mx-auto max-w-4xl px-4 py-12">
        {error && (
          <div className="mb-6 rounded-lg border border-destructive bg-destructive/10 p-4">
            <p className="text-destructive">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Package Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Service Package
              </CardTitle>
              <CardDescription>Choose your makeup service package</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="package">Package *</Label>
                <Select value={selectedPackageId} onValueChange={setSelectedPackageId}>
                  <SelectTrigger id="package">
                    <SelectValue placeholder="Select a package" />
                  </SelectTrigger>
                  <SelectContent>
                    {packages.map((pkg) => (
                      <SelectItem key={pkg.id} value={pkg.id}>
                        {pkg.name}
                        {pkg.duration_minutes && ` (${Math.floor(pkg.duration_minutes / 60)}h)`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {selectedPackage?.description && (
                  <p className="text-sm text-muted-foreground">{selectedPackage.description}</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Date, Time, and Location */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Date, Time & Location
              </CardTitle>
              <CardDescription>When and where should we meet you?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={bookingDate}
                    onChange={(e) => setBookingDate(e.target.value)}
                    min={new Date().toISOString().split("T")[0]}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="time">Time *</Label>
                  <Select value={bookingTime} onValueChange={setBookingTime}>
                    <SelectTrigger id="time">
                      <SelectValue placeholder="Select time" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 10 }, (_, i) => {
                        const hour = 8 + i;
                        const timeStr = `${hour.toString().padStart(2, "0")}:00:00`;
                        const displayTime = `${hour}:00 ${hour < 12 ? "AM" : "PM"}`;
                        return (
                          <SelectItem key={timeStr} value={timeStr}>
                            {displayTime}
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Location *</Label>
                <Select value={selectedLocationId} onValueChange={setSelectedLocationId}>
                  <SelectTrigger id="location">
                    <SelectValue placeholder="Select location" />
                  </SelectTrigger>
                  <SelectContent>
                    {locations.map((loc) => (
                      <SelectItem key={loc.id} value={loc.id}>
                        {loc.location_name}
                        {parseFloat(loc.transport_cost) > 0 && ` (+${formatCurrency(parseFloat(loc.transport_cost))})`}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Number of People */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Number of People
              </CardTitle>
              <CardDescription>How many people need makeup?</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {attendeeErrors.length > 0 && (
                <div className="rounded-lg border border-destructive bg-destructive/10 p-3">
                  {attendeeErrors.map((err, i) => (
                    <p key={i} className="text-sm text-destructive">
                      {err}
                    </p>
                  ))}
                </div>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                {selectedPackage?.base_bride_price && parseFloat(selectedPackage.base_bride_price) > 0 && (
                  <div className="space-y-2">
                    <Label htmlFor="brides">
                      Brides ({formatCurrency(parseFloat(selectedPackage.base_bride_price))} each)
                    </Label>
                    <Input
                      id="brides"
                      type="number"
                      min="0"
                      value={numBrides}
                      onChange={(e) => setNumBrides(parseInt(e.target.value) || 0)}
                    />
                  </div>
                )}

                {selectedPackage?.base_maid_price && parseFloat(selectedPackage.base_maid_price) > 0 && (
                  <div className="space-y-2">
                    <Label htmlFor="maids">
                      Maids/Bridesmaids ({formatCurrency(parseFloat(selectedPackage.base_maid_price))} each)
                    </Label>
                    <Input
                      id="maids"
                      type="number"
                      min="0"
                      value={numMaids}
                      onChange={(e) => setNumMaids(parseInt(e.target.value) || 0)}
                    />
                  </div>
                )}

                {selectedPackage?.base_mother_price && parseFloat(selectedPackage.base_mother_price) > 0 && (
                  <div className="space-y-2">
                    <Label htmlFor="mothers">
                      Mothers ({formatCurrency(parseFloat(selectedPackage.base_mother_price))} each)
                    </Label>
                    <Input
                      id="mothers"
                      type="number"
                      min="0"
                      value={numMothers}
                      onChange={(e) => setNumMothers(parseInt(e.target.value) || 0)}
                    />
                  </div>
                )}

                {selectedPackage?.base_other_price && parseFloat(selectedPackage.base_other_price) > 0 && (
                  <div className="space-y-2">
                    <Label htmlFor="others">
                      Others - Aunties, Cousins, Friends ({formatCurrency(parseFloat(selectedPackage.base_other_price))} each)
                    </Label>
                    <Input
                      id="others"
                      type="number"
                      min="0"
                      value={numOthers}
                      onChange={(e) => setNumOthers(parseInt(e.target.value) || 0)}
                    />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Additional Details */}
          <Card>
            <CardHeader>
              <CardTitle>Additional Details</CardTitle>
              <CardDescription>Tell us more about your event (optional)</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="theme">Wedding/Event Theme</Label>
                <Input
                  id="theme"
                  type="text"
                  placeholder="e.g., Rustic Garden, Modern Glam, Traditional"
                  value={weddingTheme}
                  onChange={(e) => setWeddingTheme(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="requests">Special Requests</Label>
                <Textarea
                  id="requests"
                  placeholder="Any special requirements or preferences?"
                  value={specialRequests}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setSpecialRequests(e.target.value)}
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>

          {/* Guest Information (if not logged in) */}
          {!user && (
            <Card>
              <CardHeader>
                <CardTitle>Your Contact Information</CardTitle>
                <CardDescription>We'll use this to confirm your booking</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="guestName">Full Name *</Label>
                  <Input
                    id="guestName"
                    type="text"
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="guestEmail">Email Address *</Label>
                  <Input
                    id="guestEmail"
                    type="email"
                    value={guestEmail}
                    onChange={(e) => setGuestEmail(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="guestPhone">Phone Number *</Label>
                  <Input
                    id="guestPhone"
                    type="tel"
                    placeholder="+254712345678"
                    value={guestPhone}
                    onChange={(e) => setGuestPhone(e.target.value)}
                    required
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Price Summary */}
          {pricing && (
            <Card className="border-secondary">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Price Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Subtotal:</span>
                  <span>{formatCurrency(pricing.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Transport:</span>
                  <span>{formatCurrency(pricing.transport)}</span>
                </div>
                <div className="border-t border-border pt-2">
                  <div className="flex justify-between font-semibold">
                    <span>Total:</span>
                    <span>{formatCurrency(pricing.total)}</span>
                  </div>
                  <div className="mt-2 flex justify-between text-sm">
                    <span className="text-muted-foreground">Deposit Required (50%):</span>
                    <span className="font-medium text-secondary">
                      {formatCurrency(pricing.deposit)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Submit Button */}
          <div className="flex gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={submitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!canSubmit || attendeeErrors.length > 0 || submitting}
              className="flex-1"
            >
              {submitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating Booking...
                </>
              ) : (
                "Complete Booking"
              )}
            </Button>
          </div>
        </form>
      </main>

      <Footer />
    </div>
  );
}

export default function NewBookingPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-secondary" />
      </div>
    }>
      <BookingFormContent />
    </Suspense>
  );
}
