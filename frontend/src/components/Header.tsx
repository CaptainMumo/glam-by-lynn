"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function Header() {
  const { user, authenticated, isAdmin } = useAuth();

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex items-center justify-between px-4 py-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <h1 className="text-2xl font-bold">
            <span className="text-foreground">Glam by </span>
            <span className="text-secondary">Lynn</span>
          </h1>
        </Link>

        {/* Navigation */}
        <nav className="hidden items-center gap-6 md:flex">
          <Link
            href="/"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Home
          </Link>
          <Link
            href="/services"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Services
          </Link>
          <Link
            href="/products"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Products
          </Link>
          <Link
            href="/gallery"
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Gallery
          </Link>
          {isAdmin && (
            <Link
              href="/admin"
              className="text-sm font-medium text-secondary transition-colors hover:text-secondary/80"
            >
              Admin
            </Link>
          )}
        </nav>

        {/* Auth Actions */}
        <div className="flex items-center gap-4">
          {authenticated ? (
            <>
              <div className="hidden items-center gap-2 md:flex">
                <span className="text-sm text-muted-foreground">{user?.email}</span>
                {isAdmin && (
                  <Badge variant="secondary" className="text-xs">
                    Admin
                  </Badge>
                )}
              </div>
              <Button onClick={() => signOut()} variant="outline" size="sm">
                Sign Out
              </Button>
            </>
          ) : (
            <Button asChild size="sm">
              <Link href="/auth/signin">Sign In</Link>
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}
