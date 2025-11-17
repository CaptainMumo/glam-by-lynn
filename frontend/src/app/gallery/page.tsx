/**
 * Gallery Page
 * Portfolio showcase of makeup work
 */

"use client";

import { useState } from "react";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type GalleryCategory = "all" | "bridal" | "events" | "editorial" | "classes";

interface GalleryItem {
  id: string;
  title: string;
  category: GalleryCategory;
  description: string;
}

const galleryItems: GalleryItem[] = [
  {
    id: "1",
    title: "Classic Bridal Look",
    category: "bridal",
    description: "Timeless elegance with soft glam makeup",
  },
  {
    id: "2",
    title: "Evening Gala",
    category: "events",
    description: "Bold and sophisticated makeup for a charity gala",
  },
  {
    id: "3",
    title: "Fashion Editorial",
    category: "editorial",
    description: "Creative editorial makeup for magazine shoot",
  },
  {
    id: "4",
    title: "Bohemian Bride",
    category: "bridal",
    description: "Natural, radiant bridal makeup with earthy tones",
  },
  {
    id: "5",
    title: "Student Showcase",
    category: "classes",
    description: "Amazing work from our advanced makeup class students",
  },
  {
    id: "6",
    title: "Red Carpet Ready",
    category: "events",
    description: "Glamorous look for award ceremony",
  },
  {
    id: "7",
    title: "Modern Bride",
    category: "bridal",
    description: "Contemporary bridal makeup with dewy finish",
  },
  {
    id: "8",
    title: "Avant-Garde Editorial",
    category: "editorial",
    description: "Bold artistic expression for fashion week",
  },
  {
    id: "9",
    title: "Birthday Celebration",
    category: "events",
    description: "Fresh and festive makeup for milestone birthday",
  },
];

const categories = [
  { id: "all", label: "All Work" },
  { id: "bridal", label: "Bridal" },
  { id: "events", label: "Events" },
  { id: "editorial", label: "Editorial" },
  { id: "classes", label: "Student Work" },
];

export default function GalleryPage() {
  const [selectedCategory, setSelectedCategory] = useState<GalleryCategory>("all");

  const filteredItems = selectedCategory === "all"
    ? galleryItems
    : galleryItems.filter(item => item.category === selectedCategory);

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-24">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Portfolio
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Gallery
            </h1>
            <p className="text-lg text-muted-foreground">
              Explore our portfolio of bridal makeup, special events, and creative editorial work
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
              onClick={() => setSelectedCategory(category.id as GalleryCategory)}
            >
              {category.label}
            </Button>
          ))}
        </div>

        {/* Gallery Grid - Placeholder Cards */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {filteredItems.map((item) => (
            <Card key={item.id} className="overflow-hidden">
              <div className="aspect-square bg-muted/50 flex items-center justify-center">
                <div className="text-center p-6">
                  <div className="mb-4 text-4xl text-muted-foreground/30">📸</div>
                  <p className="text-sm text-muted-foreground">
                    Image placeholder
                  </p>
                </div>
              </div>
              <CardContent className="p-4">
                <div className="mb-2">
                  <Badge variant="secondary" className="text-xs">
                    {item.category}
                  </Badge>
                </div>
                <h3 className="font-semibold">{item.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  {item.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {filteredItems.length === 0 && (
          <div className="py-16 text-center">
            <p className="text-muted-foreground">No items found in this category</p>
          </div>
        )}

        {/* Coming Soon Notice */}
        <div className="mt-16">
          <Card className="border-secondary/50 bg-muted/50">
            <CardContent className="p-8 text-center">
              <h3 className="mb-2 text-xl font-bold">Gallery Images Coming Soon</h3>
              <p className="mb-4 text-muted-foreground">
                We're currently updating our portfolio with stunning new images. Check back soon!
              </p>
              <Button variant="outline" disabled>
                Subscribe for Updates
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
