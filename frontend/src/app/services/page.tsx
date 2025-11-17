/**
 * Services Page
 * Display makeup services with booking options
 */

"use client";

import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const services = [
  {
    id: "bridal",
    title: "Bridal Makeup",
    description: "Make your special day unforgettable with professional bridal makeup artistry",
    features: [
      "Personalized consultation",
      "Trial session included",
      "Long-lasting formula",
      "Touch-up kit provided",
      "On-location service available"
    ],
    price: "Starting at $250",
    popular: true
  },
  {
    id: "events",
    title: "Special Events",
    description: "Look stunning for any occasion - from galas to photoshoots",
    features: [
      "Custom makeup design",
      "Professional application",
      "Suitable for all events",
      "Photo-ready finish",
      "Quick turnaround"
    ],
    price: "Starting at $150"
  },
  {
    id: "classes",
    title: "Makeup Classes",
    description: "Learn professional makeup techniques in personalized or group sessions",
    features: [
      "Beginner to advanced levels",
      "Hands-on training",
      "Product recommendations",
      "Take-home materials",
      "Certificate of completion"
    ],
    price: "Starting at $200"
  },
  {
    id: "consultations",
    title: "Beauty Consultations",
    description: "Get expert advice on makeup, skincare, and beauty routines",
    features: [
      "Personalized assessment",
      "Product recommendations",
      "Technique demonstrations",
      "Skincare routine planning",
      "Follow-up support"
    ],
    price: "Starting at $75"
  }
];

export default function ServicesPage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Professional Services
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Makeup Services
            </h1>
            <p className="text-lg text-muted-foreground">
              From bridal beauty to special events, we offer professional makeup artistry tailored to your unique style and occasion
            </p>
          </div>
        </div>
      </section>

      {/* Services Grid */}
      <main className="container mx-auto px-4 py-16">
        <div className="grid gap-8 md:grid-cols-2">
          {services.map((service) => (
            <Card
              key={service.id}
              id={service.id}
              className={service.popular ? "border-secondary shadow-lg" : ""}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-2xl">{service.title}</CardTitle>
                    <CardDescription className="mt-2">
                      {service.description}
                    </CardDescription>
                  </div>
                  {service.popular && (
                    <Badge variant="secondary">Popular</Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Features */}
                <div>
                  <h4 className="mb-3 font-semibold">What's Included:</h4>
                  <ul className="space-y-2">
                    {service.features.map((feature, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                        <span className="mt-1 text-secondary">✓</span>
                        <span>{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Price and CTA */}
                <div className="flex items-center justify-between border-t border-border pt-6">
                  <div>
                    <p className="text-sm text-muted-foreground">Price</p>
                    <p className="text-xl font-bold">{service.price}</p>
                  </div>
                  <Button disabled>
                    Book Now (Coming Soon)
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Call to Action */}
        <div className="mt-16">
          <Card className="border-secondary/50 bg-muted/50">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl">Ready to Book?</CardTitle>
              <CardDescription>
                Contact us to schedule your appointment or ask any questions
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center gap-4">
              <Button variant="outline" disabled>
                Contact Us (Coming Soon)
              </Button>
              <Button disabled>
                View Availability (Coming Soon)
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
