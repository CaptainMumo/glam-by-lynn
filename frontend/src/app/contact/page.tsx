/**
 * Contact Page
 * Contact form and information
 */

"use client";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Get In Touch
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Contact Us
            </h1>
            <p className="text-lg text-muted-foreground">
              Have questions about our services or ready to book? We'd love to hear from you
            </p>
          </div>
        </div>
      </section>

      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto grid max-w-5xl gap-8 lg:grid-cols-2">
          {/* Contact Form */}
          <Card>
            <CardHeader>
              <CardTitle>Send us a Message</CardTitle>
              <CardDescription>
                Fill out the form below and we'll get back to you as soon as possible
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form className="space-y-4">
                <div>
                  <label htmlFor="name" className="mb-1 block text-sm font-medium">
                    Name
                  </label>
                  <input
                    id="name"
                    type="text"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    placeholder="Your name"
                    disabled
                  />
                </div>
                <div>
                  <label htmlFor="email" className="mb-1 block text-sm font-medium">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    placeholder="your.email@example.com"
                    disabled
                  />
                </div>
                <div>
                  <label htmlFor="subject" className="mb-1 block text-sm font-medium">
                    Subject
                  </label>
                  <input
                    id="subject"
                    type="text"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    placeholder="How can we help?"
                    disabled
                  />
                </div>
                <div>
                  <label htmlFor="message" className="mb-1 block text-sm font-medium">
                    Message
                  </label>
                  <textarea
                    id="message"
                    rows={6}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                    placeholder="Tell us about your event or ask any questions..."
                    disabled
                  />
                </div>
                <Button className="w-full" disabled>
                  Send Message (Coming Soon)
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Contact Information</CardTitle>
                <CardDescription>
                  Reach out through any of these channels
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="text-2xl">📧</div>
                  <div>
                    <p className="font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">
                      info@glambylynn.com
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="text-2xl">📱</div>
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">
                      (555) 123-4567
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="text-2xl">📍</div>
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="text-sm text-muted-foreground">
                      Serving the Greater Metropolitan Area
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="text-2xl">🕒</div>
                  <div>
                    <p className="font-medium">Business Hours</p>
                    <p className="text-sm text-muted-foreground">
                      Monday - Saturday: 9am - 7pm<br />
                      Sunday: By appointment only
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="border-secondary/50">
              <CardHeader>
                <CardTitle>Booking Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <p>
                  📅 We recommend booking bridal services at least 3-6 months in advance
                </p>
                <p>
                  💰 Deposits are required to secure your appointment
                </p>
                <p>
                  🎨 Trial sessions are available for all bridal packages
                </p>
                <p>
                  🚗 On-location services available within 50 miles
                </p>
              </CardContent>
            </Card>

            <Card className="bg-muted/50">
              <CardContent className="p-6">
                <h3 className="mb-2 font-semibold">Follow Us</h3>
                <p className="mb-4 text-sm text-muted-foreground">
                  Stay updated with our latest work and beauty tips
                </p>
                <div className="flex gap-3">
                  <Button variant="outline" size="sm" disabled>
                    Instagram
                  </Button>
                  <Button variant="outline" size="sm" disabled>
                    Facebook
                  </Button>
                  <Button variant="outline" size="sm" disabled>
                    Pinterest
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
