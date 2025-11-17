import Link from "next/link";
import { Separator } from "@/components/ui/separator";

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-muted/50">
      <div className="container mx-auto px-4 py-12">
        <div className="grid gap-8 md:grid-cols-4">
          {/* Brand */}
          <div className="space-y-4">
            <h3 className="text-lg font-bold">
              <span className="text-foreground">Glam by </span>
              <span className="text-secondary">Lynn</span>
            </h3>
            <p className="text-sm text-muted-foreground">
              Professional makeup services and premium beauty products for every occasion.
            </p>
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
      </div>
    </footer>
  );
}
