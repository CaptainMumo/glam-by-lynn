/**
 * Products Catalog Page
 * Full-featured product listing with filtering, sorting, and pagination
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Grid, List, X, Search, Filter } from "lucide-react";
import { getProducts, getBrands, getCategories, type ProductFilters } from "@/lib/products";
import type { Product, Brand, Category } from "@/types";

type ViewMode = "grid" | "list";

export default function ProductsPage() {
  const router = useRouter();

  // State
  const [products, setProducts] = useState<Product[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>("grid");
  const [showFilters, setShowFilters] = useState(true);

  // Filter state
  const [filters, setFilters] = useState<ProductFilters>({
    page: 1,
    pageSize: 20,
    sortBy: "created_at",
    sortOrder: "desc",
    inStockOnly: true,
  });

  // Pagination state
  const [totalPages, setTotalPages] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);

  // Price range state
  const [priceMin, setPriceMin] = useState<string>("");
  const [priceMax, setPriceMax] = useState<string>("");

  // Fetch brands and categories on mount
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [brandsData, categoriesData] = await Promise.all([
          getBrands(),
          getCategories(),
        ]);
        setBrands(brandsData);
        setCategories(categoriesData);
      } catch (error) {
        console.error("Error fetching initial data:", error);
      }
    };

    fetchInitialData();
  }, []);

  // Fetch products whenever filters change
  useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      try {
        const data = await getProducts(filters);
        setProducts(data.items);
        setTotalPages(data.total_pages);
        setTotalProducts(data.total);
      } catch (error) {
        console.error("Error fetching products:", error);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [filters]);

  // Update filter
  const updateFilter = (key: keyof ProductFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
      page: key === "page" ? value : 1, // Reset to page 1 when changing filters
    }));
  };

  // Apply price range filter
  const applyPriceFilter = () => {
    setFilters((prev) => ({
      ...prev,
      minPrice: priceMin ? parseFloat(priceMin) : undefined,
      maxPrice: priceMax ? parseFloat(priceMax) : undefined,
      page: 1,
    }));
  };

  // Clear all filters
  const clearFilters = () => {
    setFilters({
      page: 1,
      pageSize: 20,
      sortBy: "created_at",
      sortOrder: "desc",
      inStockOnly: true,
    });
    setPriceMin("");
    setPriceMax("");
  };

  // Check if any filters are active
  const hasActiveFilters =
    filters.brandId ||
    filters.categoryId ||
    filters.search ||
    filters.minPrice !== undefined ||
    filters.maxPrice !== undefined;

  // Get active filter labels
  const getActiveFilters = () => {
    const active: { key: string; label: string; value: string }[] = [];

    if (filters.brandId) {
      const brand = brands.find((b) => b.id === filters.brandId);
      if (brand) {
        active.push({ key: "brandId", label: "Brand", value: brand.name });
      }
    }

    if (filters.categoryId) {
      const category = categories.find((c) => c.id === filters.categoryId);
      if (category) {
        active.push({ key: "categoryId", label: "Category", value: category.name });
      }
    }

    if (filters.search) {
      active.push({ key: "search", label: "Search", value: filters.search });
    }

    if (filters.minPrice !== undefined || filters.maxPrice !== undefined) {
      const min = filters.minPrice !== undefined ? `$${filters.minPrice}` : "0";
      const max = filters.maxPrice !== undefined ? `$${filters.maxPrice}` : "∞";
      active.push({ key: "price", label: "Price", value: `${min} - ${max}` });
    }

    return active;
  };

  // Remove individual filter
  const removeFilter = (key: string) => {
    if (key === "price") {
      setPriceMin("");
      setPriceMax("");
      setFilters((prev) => ({
        ...prev,
        minPrice: undefined,
        maxPrice: undefined,
        page: 1,
      }));
    } else {
      setFilters((prev) => ({
        ...prev,
        [key]: undefined,
        page: 1,
      }));
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <section className="border-b border-border bg-gradient-to-b from-background to-muted/20 px-4 py-16 md:py-20">
        <div className="container mx-auto">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="secondary" className="mb-4">
              Premium Beauty Products
            </Badge>
            <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-5xl">
              Shop Products
            </h1>
            <p className="text-lg text-muted-foreground">
              Professional-grade makeup, skincare, and beauty tools
            </p>
          </div>
        </div>
      </section>

      <main className="container mx-auto px-4 py-8">
        <div className="flex flex-col gap-8 lg:flex-row">
          {/* Filter Sidebar */}
          <aside
            className={`w-full space-y-6 lg:w-64 ${
              !showFilters ? "hidden lg:block" : ""
            }`}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">Filters</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Search */}
              <div className="space-y-2">
                <Label htmlFor="search">Search</Label>
                <div className="relative">
                  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    type="text"
                    placeholder="Search products..."
                    value={filters.search || ""}
                    onChange={(e) => updateFilter("search", e.target.value || undefined)}
                    className="pl-9"
                  />
                </div>
              </div>

              {/* Brand Filter */}
              <div className="space-y-2">
                <Label htmlFor="brand">Brand</Label>
                <Select
                  value={filters.brandId || "all"}
                  onValueChange={(value) =>
                    updateFilter("brandId", value === "all" ? undefined : value)
                  }
                >
                  <SelectTrigger id="brand">
                    <SelectValue placeholder="All brands" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All brands</SelectItem>
                    {brands.map((brand) => (
                      <SelectItem key={brand.id} value={brand.id}>
                        {brand.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Category Filter */}
              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={filters.categoryId || "all"}
                  onValueChange={(value) =>
                    updateFilter("categoryId", value === "all" ? undefined : value)
                  }
                >
                  <SelectTrigger id="category">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Price Range */}
              <div className="space-y-2">
                <Label>Price Range</Label>
                <div className="flex gap-2">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={priceMin}
                    onChange={(e) => setPriceMin(e.target.value)}
                    min="0"
                    step="0.01"
                  />
                  <Input
                    type="number"
                    placeholder="Max"
                    value={priceMax}
                    onChange={(e) => setPriceMax(e.target.value)}
                    min="0"
                    step="0.01"
                  />
                </div>
                <Button
                  size="sm"
                  onClick={applyPriceFilter}
                  className="w-full"
                  variant="outline"
                >
                  Apply
                </Button>
              </div>

              {/* In Stock Only */}
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="inStock"
                  checked={filters.inStockOnly ?? true}
                  onChange={(e) => updateFilter("inStockOnly", e.target.checked)}
                  className="rounded border-gray-300"
                />
                <Label htmlFor="inStock" className="cursor-pointer">
                  In stock only
                </Label>
              </div>

              {/* Clear Filters */}
              {hasActiveFilters && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearFilters}
                  className="w-full"
                >
                  Clear All Filters
                </Button>
              )}
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1 space-y-6">
            {/* Toolbar */}
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              {/* Results Info & Mobile Filter Toggle */}
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                  className="lg:hidden"
                >
                  <Filter className="mr-2 h-4 w-4" />
                  Filters
                </Button>
                <p className="text-sm text-muted-foreground">
                  {loading ? (
                    "Loading..."
                  ) : (
                    `Showing ${products.length} of ${totalProducts} products`
                  )}
                </p>
              </div>

              {/* View & Sort Controls */}
              <div className="flex items-center gap-3">
                {/* View Toggle */}
                <div className="flex rounded-md border">
                  <Button
                    variant={viewMode === "grid" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setViewMode("grid")}
                    className="rounded-r-none"
                  >
                    <Grid className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === "list" ? "default" : "ghost"}
                    size="sm"
                    onClick={() => setViewMode("list")}
                    className="rounded-l-none"
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>

                {/* Sort */}
                <Select
                  value={`${filters.sortBy}-${filters.sortOrder}`}
                  onValueChange={(value) => {
                    const [sortBy, sortOrder] = value.split("-");
                    setFilters((prev) => ({
                      ...prev,
                      sortBy,
                      sortOrder: sortOrder as "asc" | "desc",
                    }));
                  }}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="created_at-desc">Newest</SelectItem>
                    <SelectItem value="created_at-asc">Oldest</SelectItem>
                    <SelectItem value="base_price-asc">Price: Low to High</SelectItem>
                    <SelectItem value="base_price-desc">Price: High to Low</SelectItem>
                    <SelectItem value="title-asc">Name: A to Z</SelectItem>
                    <SelectItem value="title-desc">Name: Z to A</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Active Filters */}
            {hasActiveFilters && (
              <div className="flex flex-wrap gap-2">
                {getActiveFilters().map((filter, index) => (
                  <Badge key={index} variant="secondary" className="gap-1">
                    {filter.label}: {filter.value}
                    <button
                      onClick={() => removeFilter(filter.key)}
                      className="ml-1 hover:text-destructive"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                ))}
              </div>
            )}

            {/* Products List/Grid */}
            {loading ? (
              <div
                className={
                  viewMode === "grid"
                    ? "grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
                    : "space-y-4"
                }
              >
                {[...Array(6)].map((_, i) => (
                  <Card key={i}>
                    <CardHeader>
                      <Skeleton className="h-4 w-20" />
                      <Skeleton className="h-6 w-full" />
                      <Skeleton className="h-4 w-full" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-10 w-full" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : products.length === 0 ? (
              <div className="py-16 text-center">
                <p className="text-muted-foreground">No products found</p>
                {hasActiveFilters && (
                  <Button variant="outline" onClick={clearFilters} className="mt-4">
                    Clear Filters
                  </Button>
                )}
              </div>
            ) : (
              <div
                className={
                  viewMode === "grid"
                    ? "grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
                    : "space-y-4"
                }
              >
                {products.map((product) => (
                  <Card
                    key={product.id}
                    data-testid="product-card"
                    className={viewMode === "list" ? "product-card flex" : "product-card flex flex-col"}
                  >
                    <CardHeader className={viewMode === "list" ? "flex-1" : ""}>
                      <div className="mb-2 flex items-start justify-between">
                        <Badge variant="secondary" className="text-xs">
                          {product.category?.name || "Uncategorized"}
                        </Badge>
                        {product.isFeatured && <Badge className="text-xs">Featured</Badge>}
                      </div>
                      <CardTitle className="text-lg">{product.title}</CardTitle>
                      <CardDescription className="line-clamp-2">
                        {product.description || "No description available"}
                      </CardDescription>
                      {product.brand && (
                        <p className="text-xs text-muted-foreground">
                          Brand: {product.brand.name}
                        </p>
                      )}
                    </CardHeader>
                    <CardContent className={viewMode === "list" ? "" : "mt-auto"}>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-2xl font-bold">
                            ${parseFloat(product.basePrice.toString()).toFixed(2)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {product.inventoryCount > 0
                              ? `${product.inventoryCount} in stock`
                              : "Out of stock"}
                          </p>
                        </div>
                        <Button
                          size="sm"
                          onClick={() => router.push(`/products/${product.id}`)}
                        >
                          View Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => updateFilter("page", (filters.page ?? 1) - 1)}
                  disabled={filters.page === 1}
                >
                  Previous
                </Button>
                <div className="flex items-center gap-1">
                  {[...Array(Math.min(totalPages, 5))].map((_, i) => {
                    const pageNum = i + 1;
                    return (
                      <Button
                        key={pageNum}
                        variant={filters.page === pageNum ? "default" : "outline"}
                        size="sm"
                        onClick={() => updateFilter("page", pageNum)}
                      >
                        {pageNum}
                      </Button>
                    );
                  })}
                  {totalPages > 5 && (
                    <>
                      <span className="px-2">...</span>
                      <Button
                        variant={filters.page === totalPages ? "default" : "outline"}
                        size="sm"
                        onClick={() => updateFilter("page", totalPages)}
                      >
                        {totalPages}
                      </Button>
                    </>
                  )}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => updateFilter("page", (filters.page ?? 1) + 1)}
                  disabled={filters.page === totalPages}
                >
                  Next
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
