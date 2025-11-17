/**
 * Terms of Service Page
 */

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Legal
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Terms of Service
            </h1>
            <p className="text-lg text-muted-foreground">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </section>

      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl space-y-8">
          <Card>
            <CardHeader>
              <CardTitle>Agreement to Terms</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                By accessing and using Glam by Lynn's services, you agree to be bound by these Terms of Service
                and all applicable laws and regulations. If you do not agree with any of these terms, you are
                prohibited from using our services.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Services</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                Glam by Lynn provides professional makeup artistry services, beauty consultations, makeup
                classes, and related beauty services. Service descriptions, pricing, and availability are
                subject to change without notice.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Booking and Appointments</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-muted-foreground">
              <div>
                <h4 className="mb-2 font-semibold text-foreground">Deposits</h4>
                <p className="text-sm">
                  A 50% deposit is required to secure all bookings. Deposits are non-refundable but may
                  be transferred to a new date within 6 months of the original booking.
                </p>
              </div>
              <div>
                <h4 className="mb-2 font-semibold text-foreground">Cancellations</h4>
                <p className="text-sm">
                  Cancellations or changes must be made at least 48 hours before the scheduled appointment.
                  Late cancellations or no-shows will result in forfeiture of the deposit.
                </p>
              </div>
              <div>
                <h4 className="mb-2 font-semibold text-foreground">Late Arrivals</h4>
                <p className="text-sm">
                  Please arrive on time for your appointment. Late arrivals may result in shortened service
                  time to accommodate subsequent appointments, with no adjustment in pricing.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Payment Terms</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="mb-3 text-sm">Payment policies include:</p>
              <ul className="space-y-2 text-sm">
                <li>• 50% deposit required at time of booking</li>
                <li>• Remaining balance due on the day of service</li>
                <li>• Accepted payment methods: cash, credit/debit cards, Venmo, PayPal</li>
                <li>• Prices are subject to change; quoted price at booking time will be honored</li>
                <li>• Additional charges may apply for travel beyond standard service area</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Client Responsibilities</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="mb-3 text-sm">Clients are responsible for:</p>
              <ul className="space-y-2 text-sm">
                <li>• Providing accurate information about skin sensitivities and allergies</li>
                <li>• Arriving with clean, moisturized skin</li>
                <li>• Informing us of any changes to your booking in advance</li>
                <li>• Providing adequate space and lighting for on-location services</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Liability</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                While we take every precaution to ensure client safety and satisfaction, Glam by Lynn
                is not liable for allergic reactions to products (unless proper disclosure was not made),
                or for any damages or losses resulting from services provided. Clients with known sensitivities
                should inform us prior to service.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Intellectual Property</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                Photos and videos taken during services may be used for portfolio and marketing purposes
                unless explicitly declined by the client. All content on this website, including images,
                text, and designs, is the property of Glam by Lynn and protected by copyright laws.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Changes to Terms</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                We reserve the right to modify these terms at any time. Changes will be effective
                immediately upon posting to the website. Continued use of our services constitutes
                acceptance of modified terms.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contact Information</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                For questions about these Terms of Service, please contact us at:<br />
                Email: info@glambylynn.com<br />
                Phone: (555) 123-4567
              </p>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
