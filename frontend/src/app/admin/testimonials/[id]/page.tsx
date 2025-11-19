"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import axios from "axios";
import { useRequireAdmin } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Star } from "lucide-react";

interface ServicePackage {
  id: string;
  name: string;
}

interface Product {
  id: string;
  name: string;
}

interface Testimonial {
  id: string;
  customerName: string;
  customerPhotoUrl?: string;
  location?: string;
  rating: number;
  testimonialText: string;
  relatedServiceId?: string;
  relatedProductId?: string;
  isFeatured: boolean;
  isApproved: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export default function EditTestimonialPage() {
  const { isAdmin, loading: authLoading } = useRequireAdmin();
  const router = useRouter();
  const params = useParams();
  const testimonialId = params.id as string;

  const [formData, setFormData] = useState({
    customerName: "",
    customerPhotoUrl: "",
    location: "",
    rating: 5,
    testimonialText: "",
    relatedServiceId: "",
    relatedProductId: "",
    isFeatured: false,
    isApproved: true,
    displayOrder: 0,
  });

  const [services, setServices] = useState<ServicePackage[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAdmin && testimonialId) {
      fetchTestimonial();
      fetchServicesAndProducts();
    }
  }, [isAdmin, testimonialId]);

  const fetchTestimonial = async () => {
    try {
      setLoading(true);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) {
        setError("Authentication required");
        return;
      }

      const response = await axios.get<Testimonial>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials/${testimonialId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const testimonial = response.data;
      setFormData({
        customerName: testimonial.customerName,
        customerPhotoUrl: testimonial.customerPhotoUrl || "",
        location: testimonial.location || "",
        rating: testimonial.rating,
        testimonialText: testimonial.testimonialText,
        relatedServiceId: testimonial.relatedServiceId || "",
        relatedProductId: testimonial.relatedProductId || "",
        isFeatured: testimonial.isFeatured,
        isApproved: testimonial.isApproved,
        displayOrder: testimonial.displayOrder,
      });
    } catch (err: any) {
      console.error("Error fetching testimonial:", err);
      setError(err.response?.data?.detail || "Failed to load testimonial");
    } finally {
      setLoading(false);
    }
  };

  const fetchServicesAndProducts = async () => {
    try {
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      // Fetch services
      const servicesResponse = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/service-packages`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setServices(servicesResponse.data.items || servicesResponse.data);

      // Fetch products
      const productsResponse = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/products`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      setProducts(productsResponse.data.items || productsResponse.data);
    } catch (err) {
      console.error("Error fetching services/products:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");

    try {
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) {
        setError("Authentication required");
        return;
      }

      const payload: any = {
        customerName: formData.customerName,
        rating: formData.rating,
        testimonialText: formData.testimonialText,
        isFeatured: formData.isFeatured,
        isApproved: formData.isApproved,
        displayOrder: formData.displayOrder,
      };

      if (formData.customerPhotoUrl) {
        payload.customerPhotoUrl = formData.customerPhotoUrl;
      }

      if (formData.location) {
        payload.location = formData.location;
      }

      if (formData.relatedServiceId) {
        payload.relatedServiceId = formData.relatedServiceId;
      }

      if (formData.relatedProductId) {
        payload.relatedProductId = formData.relatedProductId;
      }

      await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials/${testimonialId}`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      router.push("/admin/testimonials");
    } catch (err: any) {
      console.error("Error updating testimonial:", err);
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to update testimonial"
      );
    } finally {
      setSaving(false);
    }
  };

  const handleRatingClick = (rating: number) => {
    setFormData((prev) => ({ ...prev, rating }));
  };

  if (authLoading || loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (error && !formData.customerName) {
    return (
      <div className="container mx-auto py-8">
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
            <Button
              className="mt-4"
              onClick={() => router.push("/admin/testimonials")}
            >
              Back to Testimonials
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Edit Testimonial</h1>
        <p className="text-muted-foreground">
          Update testimonial information
        </p>
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      <form onSubmit={handleSubmit}>
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Customer Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="customerName">
                Customer Name <span className="text-destructive">*</span>
              </Label>
              <Input
                id="customerName"
                value={formData.customerName}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    customerName: e.target.value,
                  }))
                }
                placeholder="Enter customer name"
                required
              />
            </div>

            <div>
              <Label htmlFor="customerPhotoUrl">Customer Photo URL</Label>
              <Input
                id="customerPhotoUrl"
                value={formData.customerPhotoUrl}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    customerPhotoUrl: e.target.value,
                  }))
                }
                placeholder="https://example.com/photo.jpg"
                type="url"
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Optional: URL to customer's photo
              </p>
            </div>

            <div>
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                value={formData.location}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    location: e.target.value,
                  }))
                }
                placeholder="e.g., Nairobi, Kenya"
              />
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Testimonial Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>
                Rating <span className="text-destructive">*</span>
              </Label>
              <div className="mt-2 flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => handleRatingClick(star)}
                    className="transition-transform hover:scale-110"
                  >
                    <Star
                      className={`h-8 w-8 ${
                        star <= formData.rating
                          ? "fill-yellow-400 text-yellow-400"
                          : "fill-gray-200 text-gray-200"
                      }`}
                    />
                  </button>
                ))}
                <span className="ml-2 self-center text-sm text-muted-foreground">
                  {formData.rating} star{formData.rating !== 1 ? "s" : ""}
                </span>
              </div>
            </div>

            <div>
              <Label htmlFor="testimonialText">
                Testimonial <span className="text-destructive">*</span>
              </Label>
              <Textarea
                id="testimonialText"
                value={formData.testimonialText}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    testimonialText: e.target.value,
                  }))
                }
                placeholder="Enter customer testimonial..."
                rows={6}
                required
              />
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Related Items (Optional)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="relatedServiceId">Related Service</Label>
              <Select
                value={formData.relatedServiceId}
                onValueChange={(value) =>
                  setFormData((prev) => ({
                    ...prev,
                    relatedServiceId: value,
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a service (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {services.map((service) => (
                    <SelectItem key={service.id} value={service.id}>
                      {service.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="relatedProductId">Related Product</Label>
              <Select
                value={formData.relatedProductId}
                onValueChange={(value) =>
                  setFormData((prev) => ({
                    ...prev,
                    relatedProductId: value,
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a product (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {products.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Display Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="isApproved">Approved</Label>
                <p className="text-sm text-muted-foreground">
                  Show this testimonial on the website
                </p>
              </div>
              <Switch
                id="isApproved"
                checked={formData.isApproved}
                onCheckedChange={(checked: boolean) =>
                  setFormData((prev) => ({ ...prev, isApproved: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="isFeatured">Featured</Label>
                <p className="text-sm text-muted-foreground">
                  Highlight this testimonial prominently
                </p>
              </div>
              <Switch
                id="isFeatured"
                checked={formData.isFeatured}
                onCheckedChange={(checked: boolean) =>
                  setFormData((prev) => ({ ...prev, isFeatured: checked }))
                }
              />
            </div>

            <div>
              <Label htmlFor="displayOrder">Display Order</Label>
              <Input
                id="displayOrder"
                type="number"
                min="0"
                value={formData.displayOrder}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    displayOrder: parseInt(e.target.value) || 0,
                  }))
                }
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Lower numbers appear first (0 = highest priority)
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/admin/testimonials")}
            disabled={saving}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={saving}>
            {saving ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </div>
  );
}
