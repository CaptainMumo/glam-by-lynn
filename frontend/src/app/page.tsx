"use client";

import { useAuth } from "@/hooks/useAuth";
import { signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <h1 className="text-2xl font-bold">Glam by Lynn</h1>
          <div className="flex items-center gap-4">
            {authenticated ? (
              <>
                <span className="text-sm text-muted-foreground">
                  {user?.email}
                  {isAdmin && <span className="ml-2 rounded bg-secondary px-2 py-1 text-xs">Admin</span>}
                </span>
                <Button onClick={() => signOut()} variant="outline">
                  Sign Out
                </Button>
              </>
            ) : (
              <Button asChild>
                <Link href="/auth/signin">Sign In</Link>
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="mx-auto max-w-4xl">
          {/* Welcome Section */}
          <div className="mb-12 text-center">
            <h2 className="mb-4 text-4xl font-bold">Welcome to Glam by Lynn</h2>
            <p className="text-lg text-muted-foreground">
              Professional makeup services and beauty product e-commerce
            </p>
          </div>

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
    </div>
  );
}
