/**
 * Privacy Policy Page
 */

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function PrivacyPage() {
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
              Privacy Policy
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
              <CardTitle>Introduction</CardTitle>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none text-muted-foreground">
              <p>
                At Glam by Lynn, we take your privacy seriously. This Privacy Policy explains how we collect,
                use, disclose, and safeguard your information when you use our website and services.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Information We Collect</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-muted-foreground">
              <div>
                <h4 className="mb-2 font-semibold text-foreground">Personal Information</h4>
                <p className="text-sm">
                  We may collect personal information that you provide to us, including but not limited to:
                  name, email address, phone number, and appointment details.
                </p>
              </div>
              <div>
                <h4 className="mb-2 font-semibold text-foreground">Usage Information</h4>
                <p className="text-sm">
                  We may collect information about how you access and use our website, including device
                  information, browser type, and pages visited.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>How We Use Your Information</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="mb-3 text-sm">We use the information we collect to:</p>
              <ul className="space-y-2 text-sm">
                <li>• Process and manage your bookings and appointments</li>
                <li>• Communicate with you about services and appointments</li>
                <li>• Send you promotional materials (with your consent)</li>
                <li>• Improve our website and services</li>
                <li>• Comply with legal obligations</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Information Sharing</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                We do not sell, trade, or rent your personal information to third parties. We may share
                information with service providers who assist us in operating our website and conducting
                our business, subject to confidentiality obligations.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Data Security</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                We implement appropriate technical and organizational measures to protect your personal
                information. However, no method of transmission over the Internet is 100% secure.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Your Rights</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="mb-3 text-sm">You have the right to:</p>
              <ul className="space-y-2 text-sm">
                <li>• Access the personal information we hold about you</li>
                <li>• Request correction of inaccurate information</li>
                <li>• Request deletion of your personal information</li>
                <li>• Opt-out of marketing communications</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Contact Us</CardTitle>
            </CardHeader>
            <CardContent className="text-muted-foreground">
              <p className="text-sm">
                If you have questions about this Privacy Policy, please contact us at:<br />
                Email: privacy@glambylynn.com<br />
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
