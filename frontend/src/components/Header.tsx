"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { signOut } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Search,
  ShoppingCart,
  User,
  Menu,
  ChevronDown,
  LogOut,
  Package,
  Heart,
  Settings,
  Calendar,
  Sparkles,
} from "lucide-react";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";

interface Category {
  id: string;
  name: string;
  slug: string;
}

interface SearchSuggestion {
  id: string;
  title: string;
  slug: string;
  type: "product" | "category";
}

export function Header() {
  const { user, authenticated, isAdmin } = useAuth();
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [cartItemCount, setCartItemCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchSuggestions, setSearchSuggestions] = useState<SearchSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Fetch categories on mount
  useEffect(() => {
    async function fetchCategories() {
      try {
        const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CATEGORIES.LIST}?limit=10`);
        if (res.ok) {
          const data = await res.json();
          setCategories(data);
        }
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    }
    fetchCategories();
  }, []);

  // Fetch cart count
  useEffect(() => {
    async function fetchCartCount() {
      if (!authenticated) {
        setCartItemCount(0);
        return;
      }
      try {
        const res = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CART.GET}`, {
          credentials: "include",
        });
        if (res.ok) {
          const data = await res.json();
          const count = data.items?.reduce((sum: number, item: any) => sum + item.quantity, 0) || 0;
          setCartItemCount(count);
        }
      } catch (error) {
        console.error("Error fetching cart:", error);
      }
    }
    fetchCartCount();
  }, [authenticated]);

  // Search suggestions debounced
  useEffect(() => {
    if (searchQuery.length < 2) {
      setSearchSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_BASE_URL}${API_ENDPOINTS.PRODUCTS.SEARCH}?q=${encodeURIComponent(searchQuery)}&limit=5`
        );
        if (res.ok) {
          const products = await res.json();
          const suggestions: SearchSuggestion[] = products.map((p: any) => ({
            id: p.id,
            title: p.title,
            slug: p.slug,
            type: "product" as const,
          }));
          setSearchSuggestions(suggestions);
        }
      } catch (error) {
        console.error("Error fetching suggestions:", error);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Click outside to close suggestions
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/products?q=${encodeURIComponent(searchQuery)}`);
      setSearchQuery("");
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    if (suggestion.type === "product") {
      router.push(`/products/${suggestion.slug}`);
    }
    setSearchQuery("");
    setShowSuggestions(false);
  };

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-4">
        {/* Main header */}
        <div className="flex items-center justify-between py-4">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-secondary" />
            <h1 className="text-xl font-bold md:text-2xl">
              <span className="text-foreground">Glam by </span>
              <span className="text-secondary">Lynn</span>
            </h1>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden items-center gap-6 lg:flex">
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

            {/* Categories Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-1 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground">
                  Products
                  <ChevronDown className="h-4 w-4" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48">
                <DropdownMenuItem asChild>
                  <Link href="/products" className="cursor-pointer">
                    All Products
                  </Link>
                </DropdownMenuItem>
                {categories.length > 0 && <DropdownMenuSeparator />}
                {categories.map((category) => (
                  <DropdownMenuItem key={category.id} asChild>
                    <Link
                      href={`/products?category=${category.slug}`}
                      className="cursor-pointer"
                    >
                      {category.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

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

          {/* Search, Cart, User Menu */}
          <div className="flex items-center gap-3">
            {/* Search - Desktop */}
            <div ref={searchRef} className="relative hidden md:block">
              <form onSubmit={handleSearch}>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="search"
                    placeholder="Search products..."
                    className="w-64 pl-9"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => setShowSuggestions(true)}
                  />
                </div>
              </form>

              {/* Search Suggestions */}
              {showSuggestions && searchSuggestions.length > 0 && (
                <div className="absolute top-full mt-1 w-full rounded-md border border-border bg-background shadow-lg">
                  {searchSuggestions.map((suggestion) => (
                    <button
                      key={suggestion.id}
                      className="w-full px-4 py-2 text-left text-sm hover:bg-muted"
                      onClick={() => handleSuggestionClick(suggestion)}
                    >
                      <div className="flex items-center gap-2">
                        <Search className="h-3 w-3 text-muted-foreground" />
                        <span>{suggestion.title}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Cart Icon */}
            <Button variant="ghost" size="icon" asChild className="relative">
              <Link href="/cart">
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <Badge
                    variant="secondary"
                    className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-xs"
                  >
                    {cartItemCount > 9 ? "9+" : cartItemCount}
                  </Badge>
                )}
              </Link>
            </Button>

            {/* User Menu */}
            {authenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <User className="h-5 w-5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <div className="px-2 py-1.5">
                    <p className="text-sm font-medium">{user?.name || "User"}</p>
                    <p className="text-xs text-muted-foreground">{user?.email}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/orders" className="cursor-pointer">
                      <Package className="mr-2 h-4 w-4" />
                      My Orders
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/bookings" className="cursor-pointer">
                      <Calendar className="mr-2 h-4 w-4" />
                      My Bookings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/wishlist" className="cursor-pointer">
                      <Heart className="mr-2 h-4 w-4" />
                      Wishlist
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link href="/account" className="cursor-pointer">
                      <Settings className="mr-2 h-4 w-4" />
                      Account Settings
                    </Link>
                  </DropdownMenuItem>
                  {isAdmin && (
                    <>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link href="/admin" className="cursor-pointer text-secondary">
                          <Settings className="mr-2 h-4 w-4" />
                          Admin Dashboard
                        </Link>
                      </DropdownMenuItem>
                    </>
                  )}
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    className="cursor-pointer text-red-600"
                    onClick={() => signOut()}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign Out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button asChild size="sm">
                <Link href="/auth/signin">Sign In</Link>
              </Button>
            )}

            {/* Mobile Menu */}
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-80">
                <SheetHeader>
                  <SheetTitle>
                    <span className="text-foreground">Glam by </span>
                    <span className="text-secondary">Lynn</span>
                  </SheetTitle>
                </SheetHeader>

                {/* Mobile Search */}
                <div className="my-6">
                  <form onSubmit={handleSearch}>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        type="search"
                        placeholder="Search products..."
                        className="pl-9"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                  </form>
                </div>

                {/* Mobile Navigation */}
                <nav className="flex flex-col gap-4">
                  <Link
                    href="/"
                    className="text-sm font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Home
                  </Link>
                  <Link
                    href="/services"
                    className="text-sm font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Services
                  </Link>
                  <Link
                    href="/products"
                    className="text-sm font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Products
                  </Link>

                  {/* Mobile Categories */}
                  {categories.length > 0 && (
                    <div className="ml-4 flex flex-col gap-2">
                      {categories.map((category) => (
                        <Link
                          key={category.id}
                          href={`/products?category=${category.slug}`}
                          className="text-sm text-muted-foreground"
                          onClick={() => setMobileMenuOpen(false)}
                        >
                          {category.name}
                        </Link>
                      ))}
                    </div>
                  )}

                  <Link
                    href="/gallery"
                    className="text-sm font-medium"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Gallery
                  </Link>

                  {authenticated && (
                    <>
                      <hr className="my-2" />
                      <Link
                        href="/orders"
                        className="text-sm font-medium"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        My Orders
                      </Link>
                      <Link
                        href="/bookings"
                        className="text-sm font-medium"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        My Bookings
                      </Link>
                      <Link
                        href="/wishlist"
                        className="text-sm font-medium"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Wishlist
                      </Link>
                    </>
                  )}

                  {isAdmin && (
                    <>
                      <hr className="my-2" />
                      <Link
                        href="/admin"
                        className="text-sm font-medium text-secondary"
                        onClick={() => setMobileMenuOpen(false)}
                      >
                        Admin Dashboard
                      </Link>
                    </>
                  )}
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}
