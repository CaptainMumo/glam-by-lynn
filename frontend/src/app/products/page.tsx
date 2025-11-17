/**
 * Products Page
 * Display beauty products catalog
 */

"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type ProductCategory = "all" | "makeup" | "skincare" | "tools";

interface Product {
  id: string;
  name: string;
  category: ProductCategory;
  price: number;
  description: string;
  featured?: boolean;
}

const products: Product[] = [
  {
    id: "1",
    name: "Professional Makeup Brush Set",
    category: "tools",
    price: 89.99,
    description: "12-piece premium brush collection for flawless application",
    featured: true
  },
  {
    id: "2",
    name: "Long-Wear Foundation",
    category: "makeup",
    price: 45.00,
    description: "24-hour wear with buildable, natural coverage",
    featured: true
  },
  {
    id: "3",
    name: "Hydrating Serum",
    category: "skincare",
    price: 65.00,
    description: "Intensive hydration with hyaluronic acid",
  },
  {
    id: "4",
    name: "Eyeshadow Palette",
    category: "makeup",
    price: 52.00,
    description: "20 versatile shades for day to night looks",
  },
  {
    id: "5",
    name: "Vitamin C Moisturizer",
    category: "skincare",
    price: 48.00,
    description: "Brightening and anti-aging daily moisturizer",
    featured: true
  },
  {
    id: "6",
    name: "Makeup Sponge Set",
    category: "tools",
    price: 24.99,
    description: "Latex-free blending sponges for seamless application",
  },
  {
    id: "7",
    name: "Matte Lipstick Collection",
    category: "makeup",
    price: 38.00,
    description: "Set of 5 long-lasting matte lip colors",
  },
  {
    id: "8",
    name: "Facial Cleansing Oil",
    category: "skincare",
    price: 32.00,
    description: "Gentle makeup remover and deep cleanser",
  },
];

const categories = [
  { id: "all", label: "All Products" },
  { id: "makeup", label: "Makeup" },
  { id: "skincare", label: "Skincare" },
  { id: "tools", label: "Tools & Brushes" },
];

export default function ProductsPage() {
  const [selectedCategory, setSelectedCategory] = useState<ProductCategory>("all");

  const filteredProducts = selectedCategory === "all"
    ? products
    : products.filter(p => p.category === selectedCategory);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Premium Beauty Products
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Shop Products
            </h1>
            <p className="text-lg text-muted-foreground">
              Curated selection of professional-grade makeup, skincare, and beauty tools
            </p>
          </div>
        </div>
      </section>

      <main className="container mx-auto px-4 py-16">
        {/* Category Filter */}
        <div className="mb-8 flex flex-wrap justify-center gap-3">
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "outline"}
              onClick={() => setSelectedCategory(category.id as ProductCategory)}
            >
              {category.label}
            </Button>
          ))}
        </div>

        {/* Products Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="flex flex-col">
              <CardHeader>
                <div className="mb-2 flex items-start justify-between">
                  <Badge variant="secondary" className="text-xs">
                    {product.category}
                  </Badge>
                  {product.featured && (
                    <Badge className="text-xs">Featured</Badge>
                  )}
                </div>
                <CardTitle className="text-lg">{product.name}</CardTitle>
                <CardDescription className="line-clamp-2">
                  {product.description}
                </CardDescription>
              </CardHeader>
              <CardContent className="mt-auto">
                <div className="flex items-center justify-between">
                  <p className="text-2xl font-bold">
                    ${product.price.toFixed(2)}
                  </p>
                  <Button size="sm" disabled>
                    Add to Cart
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredProducts.length === 0 && (
          <div className="py-16 text-center">
            <p className="text-muted-foreground">No products found in this category</p>
          </div>
        )}

        {/* Coming Soon Notice */}
        <div className="mt-16">
          <Card className="border-secondary/50 bg-muted/50">
            <CardHeader className="text-center">
              <CardTitle>Online Store Coming Soon</CardTitle>
              <CardDescription>
                We're working on bringing you a seamless online shopping experience. Stay tuned!
              </CardDescription>
            </CardHeader>
            <CardContent className="flex justify-center">
              <Button variant="outline" disabled>
                Notify Me When Available
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
