"use client";

import Link from "next/link";
import { useState } from "react";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Mail, Facebook, Instagram, Twitter, Youtube, CreditCard, Smartphone } from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();
  const [email, setEmail] = useState("");
  const [subscribeStatus, setSubscribeStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setSubscribeStatus("loading");
    // TODO: Implement newsletter subscription API call
    // For now, just simulate success
    setTimeout(() => {
      setSubscribeStatus("success");
      setEmail("");
      setTimeout(() => setSubscribeStatus("idle"), 3000);
    }, 1000);
  };

  return (
    <footer className="border-t border-border bg-muted/50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid gap-8 md:grid-cols-4">
          {/* Brand & Newsletter */}
          <div className="space-y-4 md:col-span-1">
            <h3 className="text-lg font-bold">
              <span className="text-foreground">Glam by </span>
              <span className="text-secondary">Lynn</span>
            </h3>
            <p className="text-sm text-muted-foreground">
              Professional makeup services and premium beauty products for every occasion.
            </p>

            {/* Newsletter Signup */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold">Subscribe to our newsletter</h4>
              <form onSubmit={handleNewsletterSubmit} className="flex gap-2">
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="flex-1"
                  disabled={subscribeStatus === "loading"}
                  required
                />
                <Button
                  type="submit"
                  size="icon"
                  disabled={subscribeStatus === "loading"}
                  className="shrink-0"
                >
                  <Mail className="h-4 w-4" />
                </Button>
              </form>
              {subscribeStatus === "success" && (
                <p className="text-xs text-secondary">Successfully subscribed!</p>
              )}
              {subscribeStatus === "error" && (
                <p className="text-xs text-destructive">Failed to subscribe. Please try again.</p>
              )}
            </div>

            {/* Social Media Links */}
            <div className="space-y-2">
              <h4 className="text-sm font-semibold">Follow Us</h4>
              <div className="flex gap-3">
                <Link
                  href="https://facebook.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-secondary transition-colors"
                  aria-label="Facebook"
                >
                  <Facebook className="h-5 w-5" />
                </Link>
                <Link
                  href="https://instagram.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-secondary transition-colors"
                  aria-label="Instagram"
                >
                  <Instagram className="h-5 w-5" />
                </Link>
                <Link
                  href="https://twitter.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-secondary transition-colors"
                  aria-label="Twitter"
                >
                  <Twitter className="h-5 w-5" />
                </Link>
                <Link
                  href="https://youtube.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-secondary transition-colors"
                  aria-label="YouTube"
                >
                  <Youtube className="h-5 w-5" />
                </Link>
              </div>
            </div>
          </div>

          {/* Services */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Services</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="/services#bridal" className="hover:text-foreground">
                  Bridal Makeup
                </Link>
              </li>
              <li>
                <Link href="/services#events" className="hover:text-foreground">
                  Special Events
                </Link>
              </li>
              <li>
                <Link href="/services#classes" className="hover:text-foreground">
                  Makeup Classes
                </Link>
              </li>
              <li>
                <Link href="/services#consultations" className="hover:text-foreground">
                  Consultations
                </Link>
              </li>
            </ul>
          </div>

          {/* Shop */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Shop</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="/products" className="hover:text-foreground">
                  All Products
                </Link>
              </li>
              <li>
                <Link href="/products?category=makeup" className="hover:text-foreground">
                  Makeup
                </Link>
              </li>
              <li>
                <Link href="/products?category=skincare" className="hover:text-foreground">
                  Skincare
                </Link>
              </li>
              <li>
                <Link href="/products?category=tools" className="hover:text-foreground">
                  Tools & Brushes
                </Link>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold">Company</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link href="/about" className="hover:text-foreground">
                  About Us
                </Link>
              </li>
              <li>
                <Link href="/gallery" className="hover:text-foreground">
                  Gallery
                </Link>
              </li>
              <li>
                <Link href="/contact" className="hover:text-foreground">
                  Contact
                </Link>
              </li>
              <li>
                <Link href="/faq" className="hover:text-foreground">
                  FAQ
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <Separator className="my-8" />

        {/* Bottom */}
        <div className="space-y-4">
          <div className="flex flex-col items-center justify-between gap-4 text-sm text-muted-foreground md:flex-row">
            <p>&copy; {currentYear} Glam by Lynn. All rights reserved.</p>
            <div className="flex gap-6">
              <Link href="/privacy" className="hover:text-foreground">
                Privacy Policy
              </Link>
              <Link href="/terms" className="hover:text-foreground">
                Terms of Service
              </Link>
            </div>
          </div>

          {/* Payment Methods */}
          <div className="flex flex-col items-center gap-3 border-t border-border pt-4 md:flex-row md:justify-between">
            <p className="text-xs text-muted-foreground">We accept:</p>
            <div className="flex items-center gap-4">
              {/* M-Pesa */}
              <div className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3 py-1.5">
                <Smartphone className="h-4 w-4 text-green-600" />
                <span className="text-xs font-semibold text-green-600">M-PESA</span>
              </div>

              {/* Credit/Debit Cards */}
              <div className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3 py-1.5">
                <CreditCard className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground">Visa</span>
              </div>

              <div className="flex items-center gap-1.5 rounded-md border border-border bg-background px-3 py-1.5">
                <CreditCard className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs font-medium text-muted-foreground">Mastercard</span>
              </div>

              {/* Bank Transfer */}
              <div className="rounded-md border border-border bg-background px-3 py-1.5">
                <span className="text-xs font-medium text-muted-foreground">Bank Transfer</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
