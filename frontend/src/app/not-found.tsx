"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Search, Home, ArrowLeft } from "lucide-react";

/**
 * 404 Not Found Page
 * Displayed when a page route doesn't exist
 */
export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex flex-1 items-center justify-center bg-background px-4 py-16">
        <div className="w-full max-w-2xl space-y-8 text-center">
          {/* 404 Illustration */}
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className="rounded-full bg-secondary/10 p-6">
                <Search className="h-16 w-16 text-secondary" />
              </div>
            </div>

            <div className="space-y-2">
              <h1 className="text-6xl font-bold tracking-tight">404</h1>
              <h2 className="text-2xl font-semibold tracking-tight">
                Page Not Found
              </h2>
              <p className="text-muted-foreground">
                Sorry, we couldn't find the page you're looking for. The page may have been moved or deleted.
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
            <Button asChild size="lg">
              <Link href="/">
                <Home className="mr-2 h-4 w-4" />
                Go to Homepage
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <button type="button" onClick={() => window.history.back()}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </button>
            </Button>
          </div>

          {/* Quick Links */}
          <div className="border-t border-border pt-8">
            <p className="mb-4 text-sm font-semibold text-muted-foreground">
              You might be looking for:
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <Link
                href="/services"
                className="text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                Services
              </Link>
              <Link
                href="/products"
                className="text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                Products
              </Link>
              <Link
                href="/gallery"
                className="text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                Gallery
              </Link>
              <Link
                href="/about"
                className="text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                About Us
              </Link>
              <Link
                href="/contact"
                className="text-muted-foreground hover:text-foreground underline underline-offset-4"
              >
                Contact
              </Link>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
