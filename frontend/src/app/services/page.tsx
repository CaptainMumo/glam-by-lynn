/**
 * Services Page
 * Display makeup service packages with booking options
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ServicePackage } from "@/types";
import {
  getActiveServicePackages,
  getPackageTypeName,
  getPricingDescription,
  getPackageFeatures,
} from "@/lib/services";
import { Loader2 } from "lucide-react";

export default function ServicesPage() {
  const router = useRouter();
  const [packages, setPackages] = useState<ServicePackage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPackages() {
      try {
        setLoading(true);
        const data = await getActiveServicePackages();
        setPackages(data);
      } catch (err) {
        console.error("Failed to fetch service packages:", err);
        setError("Failed to load service packages. Please try again later.");
      } finally {
        setLoading(false);
      }
    }

    fetchPackages();
  }, []);

  const handleBookNow = (packageId: string) => {
    // TODO: Navigate to booking form with package pre-selected
    router.push(`/bookings/new?packageId=${packageId}`);
  };

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
        {loading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-secondary" />
          </div>
        ) : error ? (
          <div className="mx-auto max-w-md rounded-lg border border-destructive bg-destructive/10 p-6 text-center">
            <p className="text-destructive">{error}</p>
          </div>
        ) : packages.length === 0 ? (
          <div className="mx-auto max-w-md rounded-lg border border-border bg-muted/50 p-6 text-center">
            <p className="text-muted-foreground">
              No service packages available at the moment. Please check back later.
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-8 md:grid-cols-2">
              {packages.map((pkg) => {
                const features = getPackageFeatures(pkg);
                const pricingDescription = getPricingDescription(pkg);
                const isPopular = pkg.packageType === "bridal_large" || pkg.packageType === "bride_only";

                return (
                  <Card
                    key={pkg.id}
                    id={pkg.id}
                    data-testid="service-card"
                    className={isPopular ? "service-card package-card border-secondary shadow-lg" : "service-card package-card"}
                  >
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-2xl">{pkg.name}</CardTitle>
                          {pkg.description && (
                            <CardDescription className="mt-2">
                              {pkg.description}
                            </CardDescription>
                          )}
                        </div>
                        {isPopular && (
                          <Badge variant="secondary">Popular</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      {/* Features */}
                      <div>
                        <h4 className="mb-3 font-semibold">What's Included:</h4>
                        <ul className="space-y-2">
                          {features.map((feature, index) => (
                            <li key={index} className="flex items-start gap-2 text-sm text-muted-foreground">
                              <span className="mt-1 text-secondary">✓</span>
                              <span>{feature}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Price and CTA */}
                      <div className="flex flex-col gap-4 border-t border-border pt-6">
                        <div>
                          <p className="text-sm text-muted-foreground">Pricing</p>
                          <p className="text-sm font-semibold">{pricingDescription}</p>
                        </div>
                        <Button
                          onClick={() => handleBookNow(pkg.id)}
                          className="w-full"
                        >
                          Book Now
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Call to Action */}
            <div className="mt-16">
              <Card className="border-secondary/50 bg-muted/50">
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">Ready to Book?</CardTitle>
                  <CardDescription>
                    Choose a service package above to get started or contact us for personalized recommendations
                  </CardDescription>
                </CardHeader>
                <CardContent className="flex justify-center gap-4">
                  <Button variant="outline" onClick={() => router.push("/contact")}>
                    Contact Us
                  </Button>
                  <Button onClick={() => router.push("/bookings/availability")}>
                    Check Availability
                  </Button>
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </main>

      <Footer />
    </div>
  );
}
