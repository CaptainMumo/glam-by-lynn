"use client";

import { useState, useEffect } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import Image from "next/image";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";
import { Star, ArrowRight, CheckCircle, Sparkles, ShoppingBag, Heart } from "lucide-react";

interface Product {
  id: string;
  title: string;
  slug: string;
  description?: string;
  base_price: number;
  images?: Array<{ url: string; alt_text?: string }>;
  brand?: { name: string };
  average_rating?: number;
  review_count?: number;
}

interface Category {
  id: string;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  product_count?: number;
}

interface Testimonial {
  id: string;
  author_name: string;
  content: string;
  rating: number;
  service_type?: string;
  is_featured: boolean;
}

export default function Home() {
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [newsletterEmail, setNewsletterEmail] = useState("");
  const [newsletterStatus, setNewsletterStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        // Fetch featured products
        const productsRes = await fetch(`${API_BASE_URL}${API_ENDPOINTS.PRODUCTS.FEATURED}?limit=6`);
        if (productsRes.ok) {
          const productsData = await productsRes.json();
          setFeaturedProducts(productsData);
        }

        // Fetch categories
        const categoriesRes = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CATEGORIES.LIST}?limit=4`);
        if (categoriesRes.ok) {
          const categoriesData = await categoriesRes.json();
          setCategories(categoriesData);
        }

        // Fetch featured testimonials
        const testimonialsRes = await fetch(`${API_BASE_URL}${API_ENDPOINTS.TESTIMONIALS.FEATURED}?limit=3`);
        if (testimonialsRes.ok) {
          const testimonialsData = await testimonialsRes.json();
          setTestimonials(testimonialsData);
        }
      } catch (error) {
        console.error("Error fetching homepage data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const handleNewsletterSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setNewsletterStatus("loading");

    // Simulate newsletter subscription (backend endpoint would be needed)
    try {
      // TODO: Implement backend newsletter endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      setNewsletterStatus("success");
      setNewsletterEmail("");
      setTimeout(() => setNewsletterStatus("idle"), 3000);
    } catch (error) {
      setNewsletterStatus("error");
      setTimeout(() => setNewsletterStatus("idle"), 3000);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-background via-muted/30 to-secondary/10">
        <div className="absolute inset-0 bg-grid-pattern opacity-5" />
        <div className="container relative mx-auto px-4 py-20 md:py-32">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-6 px-4 py-2">
              <Sparkles className="mr-2 h-4 w-4 inline" />
              Premium Beauty Services & Products
            </Badge>
            <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-7xl">
              <span className="text-foreground">Glam by</span>{" "}
              <span className="text-secondary">Lynn</span>
            </h1>
            <p className="mb-8 text-lg text-muted-foreground md:text-xl lg:text-2xl">
              Professional makeup artistry and curated beauty products
              <br className="hidden md:block" />
              for your most special moments
            </p>
            <div className="flex flex-col justify-center gap-4 sm:flex-row">
              <Button asChild size="lg" className="group">
                <Link href="/services">
                  Book a Service
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="group">
                <Link href="/products">
                  <ShoppingBag className="mr-2 h-4 w-4" />
                  Shop Products
                </Link>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="mt-12 flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-secondary" />
                <span>Professional Certified</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-secondary" />
                <span>Premium Products</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-secondary" />
                <span>Based in Nairobi & Kitui</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <main>
        {/* Featured Products Section */}
        <section className="border-b border-border bg-background py-16 md:py-20">
          <div className="container mx-auto px-4">
            <div className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                Featured Products
              </h2>
              <p className="text-lg text-muted-foreground">
                Discover our curated selection of premium beauty essentials
              </p>
            </div>

            {loading ? (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {[...Array(6)].map((_, i) => (
                  <Card key={i} className="overflow-hidden">
                    <div className="aspect-square animate-pulse bg-muted" />
                    <CardHeader>
                      <div className="h-6 w-3/4 animate-pulse rounded bg-muted" />
                    </CardHeader>
                  </Card>
                ))}
              </div>
            ) : featuredProducts.length > 0 ? (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {featuredProducts.map((product) => (
                  <Card key={product.id} className="group overflow-hidden transition-all hover:shadow-lg">
                    <Link href={`/products/${product.slug}`}>
                      <div className="relative aspect-square overflow-hidden bg-muted">
                        {product.images && product.images[0] ? (
                          <Image
                            src={product.images[0].url}
                            alt={product.images[0].alt_text || product.title}
                            fill
                            className="object-cover transition-transform group-hover:scale-105"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center">
                            <Heart className="h-12 w-12 text-muted-foreground/30" />
                          </div>
                        )}
                        <div className="absolute right-2 top-2">
                          <Badge variant="secondary">Featured</Badge>
                        </div>
                      </div>
                      <CardHeader>
                        <CardTitle className="line-clamp-2 text-lg">
                          {product.title}
                        </CardTitle>
                        {product.brand && (
                          <p className="text-sm text-muted-foreground">
                            {product.brand.name}
                          </p>
                        )}
                      </CardHeader>
                      <CardContent>
                        <div className="flex items-center justify-between">
                          <span className="text-2xl font-bold">
                            KSh {product.base_price.toLocaleString()}
                          </span>
                          {product.average_rating && (
                            <div className="flex items-center gap-1">
                              <Star className="h-4 w-4 fill-secondary text-secondary" />
                              <span className="text-sm font-medium">
                                {product.average_rating.toFixed(1)}
                              </span>
                              {product.review_count && (
                                <span className="text-sm text-muted-foreground">
                                  ({product.review_count})
                                </span>
                              )}
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Link>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-muted-foreground">
                <ShoppingBag className="mx-auto mb-4 h-12 w-12 opacity-50" />
                <p>Featured products coming soon</p>
              </div>
            )}

            <div className="mt-10 text-center">
              <Button asChild size="lg" variant="outline">
                <Link href="/products">
                  View All Products
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Categories Section */}
        <section className="bg-muted/30 py-16 md:py-20">
          <div className="container mx-auto px-4">
            <div className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                Shop by Category
              </h2>
              <p className="text-lg text-muted-foreground">
                Find exactly what you're looking for
              </p>
            </div>

            {categories.length > 0 ? (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {categories.map((category) => (
                  <Link key={category.id} href={`/products?category=${category.slug}`}>
                    <Card className="group cursor-pointer overflow-hidden transition-all hover:shadow-lg">
                      <div className="relative aspect-square overflow-hidden bg-gradient-to-br from-secondary/20 to-muted">
                        {category.image_url ? (
                          <Image
                            src={category.image_url}
                            alt={category.name}
                            fill
                            className="object-cover transition-transform group-hover:scale-105"
                          />
                        ) : (
                          <div className="flex h-full items-center justify-center">
                            <Sparkles className="h-16 w-16 text-muted-foreground/30" />
                          </div>
                        )}
                      </div>
                      <CardHeader>
                        <CardTitle className="text-center">{category.name}</CardTitle>
                        {category.product_count !== undefined && (
                          <p className="text-center text-sm text-muted-foreground">
                            {category.product_count} products
                          </p>
                        )}
                      </CardHeader>
                    </Card>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {["Makeup", "Skincare", "Tools", "Accessories"].map((name) => (
                  <Card key={name} className="overflow-hidden">
                    <div className="aspect-square bg-gradient-to-br from-secondary/20 to-muted" />
                    <CardHeader>
                      <CardTitle className="text-center">{name}</CardTitle>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="border-t border-border py-16 md:py-20">
          <div className="container mx-auto px-4">
            <div className="mb-12 text-center">
              <h2 className="mb-4 text-3xl font-bold md:text-4xl">
                What Our Clients Say
              </h2>
              <p className="text-lg text-muted-foreground">
                Real experiences from real people
              </p>
            </div>

            {testimonials.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {testimonials.map((testimonial) => (
                  <Card key={testimonial.id} className="flex flex-col">
                    <CardHeader>
                      <div className="mb-2 flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`h-4 w-4 ${
                              i < testimonial.rating
                                ? "fill-secondary text-secondary"
                                : "text-muted"
                            }`}
                          />
                        ))}
                      </div>
                      <CardTitle className="text-lg">{testimonial.author_name}</CardTitle>
                      {testimonial.service_type && (
                        <p className="text-sm text-muted-foreground">
                          {testimonial.service_type}
                        </p>
                      )}
                    </CardHeader>
                    <CardContent className="flex-1">
                      <p className="text-muted-foreground">"{testimonial.content}"</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="py-12 text-center text-muted-foreground">
                <Star className="mx-auto mb-4 h-12 w-12 opacity-50" />
                <p>Client testimonials coming soon</p>
              </div>
            )}

            <div className="mt-10 text-center">
              <Button asChild variant="outline" size="lg">
                <Link href="/gallery">
                  View Our Work
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Newsletter Section */}
        <section className="bg-gradient-to-br from-secondary/10 via-background to-muted/20 py-16 md:py-20">
          <div className="container mx-auto px-4">
            <Card className="mx-auto max-w-2xl border-2 border-secondary/20">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl md:text-3xl">
                  Join Our Beauty Community
                </CardTitle>
                <p className="text-muted-foreground">
                  Get exclusive tips, product launches, and special offers delivered to your inbox
                </p>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleNewsletterSubmit} className="flex flex-col gap-4 sm:flex-row">
                  <Input
                    type="email"
                    placeholder="Enter your email"
                    value={newsletterEmail}
                    onChange={(e) => setNewsletterEmail(e.target.value)}
                    required
                    disabled={newsletterStatus === "loading"}
                    className="flex-1"
                  />
                  <Button
                    type="submit"
                    disabled={newsletterStatus === "loading"}
                    className="whitespace-nowrap"
                  >
                    {newsletterStatus === "loading" ? "Subscribing..." : "Subscribe"}
                  </Button>
                </form>
                {newsletterStatus === "success" && (
                  <div className="mt-4 flex items-center justify-center gap-2 text-sm text-green-600">
                    <CheckCircle className="h-4 w-4" />
                    <span>Successfully subscribed! Check your inbox.</span>
                  </div>
                )}
                {newsletterStatus === "error" && (
                  <div className="mt-4 text-center text-sm text-red-600">
                    Something went wrong. Please try again.
                  </div>
                )}
              </CardContent>
              <CardFooter className="justify-center text-xs text-muted-foreground">
                We respect your privacy. Unsubscribe at any time.
              </CardFooter>
            </Card>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
