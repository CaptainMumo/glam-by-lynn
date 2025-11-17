"use client";

import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import Link from "next/link";

export default function Home() {
  const { user, loading, authenticated, isAdmin } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 text-lg">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-20 md:py-32">
        <div className="container mx-auto">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-4">
              Premium Beauty Services
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
              Your Beauty, <span className="text-secondary">Elevated</span>
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl">
              Professional makeup artistry and curated beauty products for every special moment
            </p>
            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/services">Book a Service</Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <Link href="/products">Shop Products</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-6xl">

          {/* User Status Card */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Authentication Status</CardTitle>
              <CardDescription>Current session information</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="font-medium">Status:</span>
                <span className={authenticated ? "text-green-600" : "text-muted-foreground"}>
                  {authenticated ? "Authenticated" : "Not authenticated"}
                </span>
              </div>
              {authenticated && user && (
                <>
                  <div className="flex justify-between">
                    <span className="font-medium">Email:</span>
                    <span>{user.email}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Name:</span>
                    <span>{user.name || "N/A"}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">User ID:</span>
                    <span className="font-mono text-xs">{user.id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="font-medium">Admin:</span>
                    <span>{isAdmin ? `Yes (${user.adminRole})` : "No"}</span>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Makeup Services</CardTitle>
                <CardDescription>Book professional makeup appointments</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Bridal makeup, special events, and makeup classes available
                </p>
                <Button className="mt-4" variant="secondary" disabled>
                  Coming Soon
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Beauty Products</CardTitle>
                <CardDescription>Shop premium beauty products</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Curated selection of professional makeup and skincare
                </p>
                <Button className="mt-4" variant="secondary" disabled>
                  Coming Soon
                </Button>
              </CardContent>
            </Card>

            {isAdmin && (
              <Card className="border-secondary md:col-span-2">
                <CardHeader>
                  <CardTitle>Admin Panel</CardTitle>
                  <CardDescription>Manage products, bookings, and content</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    Access admin features to manage the platform
                  </p>
                  <Button className="mt-4" disabled>
                    Go to Admin Dashboard (Coming Soon)
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          {/* API Status */}
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>Backend API connection</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <span>Backend API:</span>
                <span className="text-sm text-muted-foreground">
                  {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                </span>
              </div>
              <div className="mt-4 text-center">
                <Button variant="outline" asChild>
                  <Link href={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/docs`} target="_blank">
                    View API Docs
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
