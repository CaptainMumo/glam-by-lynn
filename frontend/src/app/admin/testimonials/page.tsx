"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { useRequireAdmin } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Pencil, Trash2, Star, StarOff, CheckCircle, XCircle } from "lucide-react";

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

interface TestimonialListResponse {
  items: Testimonial[];
  total: number;
}

export default function TestimonialsPage() {
  const { isAdmin, loading: authLoading } = useRequireAdmin();
  const router = useRouter();
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [togglingId, setTogglingId] = useState<string | null>(null);

  // Filters
  const [approvalFilter, setApprovalFilter] = useState<string>("all");
  const [featuredFilter, setFeaturedFilter] = useState<string>("all");

  const fetchTestimonials = async () => {
    if (!isAdmin) return;

    try {
      setLoading(true);
      setError("");

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) {
        setError("Authentication required");
        return;
      }

      const params = new URLSearchParams();

      if (approvalFilter !== "all") {
        params.append("isApproved", approvalFilter);
      }

      if (featuredFilter !== "all") {
        params.append("isFeatured", featuredFilter);
      }

      const response = await axios.get<TestimonialListResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setTestimonials(response.data.items);
      setTotal(response.data.total);
    } catch (err: any) {
      console.error("Error fetching testimonials:", err);
      setError(err.response?.data?.detail || "Failed to load testimonials");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTestimonials();
  }, [isAdmin, approvalFilter, featuredFilter]);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this testimonial?")) {
      return;
    }

    try {
      setDeletingId(id);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      await fetchTestimonials();
    } catch (err: any) {
      console.error("Error deleting testimonial:", err);
      alert(err.response?.data?.detail || "Failed to delete testimonial");
    } finally {
      setDeletingId(null);
    }
  };

  const handleToggleFeatured = async (testimonial: Testimonial) => {
    try {
      setTogglingId(testimonial.id);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials/${testimonial.id}`,
        {
          isFeatured: !testimonial.isFeatured,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      await fetchTestimonials();
    } catch (err: any) {
      console.error("Error toggling featured status:", err);
      alert(err.response?.data?.detail || "Failed to update testimonial");
    } finally {
      setTogglingId(null);
    }
  };

  const handleToggleApproval = async (testimonial: Testimonial) => {
    try {
      setTogglingId(testimonial.id);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/testimonials/${testimonial.id}/approve`,
        {
          isApproved: !testimonial.isApproved,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      await fetchTestimonials();
    } catch (err: any) {
      console.error("Error toggling approval status:", err);
      alert(err.response?.data?.detail || "Failed to update testimonial");
    } finally {
      setTogglingId(null);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`h-4 w-4 ${
              star <= rating
                ? "fill-yellow-400 text-yellow-400"
                : "fill-gray-200 text-gray-200"
            }`}
          />
        ))}
      </div>
    );
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

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Testimonials</h1>
          <p className="text-muted-foreground">
            Manage customer testimonials and reviews
          </p>
        </div>
        <Button onClick={() => router.push("/admin/testimonials/new")}>
          Add Testimonial
        </Button>
      </div>

      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
          </CardContent>
        </Card>
      )}

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <label className="mb-2 block text-sm font-medium">
                Approval Status
              </label>
              <Select
                value={approvalFilter}
                onValueChange={setApprovalFilter}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All testimonials" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All testimonials</SelectItem>
                  <SelectItem value="true">Approved only</SelectItem>
                  <SelectItem value="false">Pending approval</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Featured Status
              </label>
              <Select
                value={featuredFilter}
                onValueChange={setFeaturedFilter}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All testimonials" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All testimonials</SelectItem>
                  <SelectItem value="true">Featured only</SelectItem>
                  <SelectItem value="false">Not featured</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            {total} Testimonial{total !== 1 ? "s" : ""}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {testimonials.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              No testimonials found. Create your first testimonial to get
              started.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Customer</TableHead>
                    <TableHead>Rating</TableHead>
                    <TableHead>Testimonial</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead className="text-center">Status</TableHead>
                    <TableHead className="text-center">Featured</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {testimonials.map((testimonial) => (
                    <TableRow key={testimonial.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          {testimonial.customerPhotoUrl ? (
                            <img
                              src={testimonial.customerPhotoUrl}
                              alt={testimonial.customerName}
                              className="h-10 w-10 rounded-full object-cover"
                            />
                          ) : (
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                              <span className="text-sm font-medium">
                                {testimonial.customerName.charAt(0)}
                              </span>
                            </div>
                          )}
                          <div>
                            <p className="font-medium">
                              {testimonial.customerName}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{renderStars(testimonial.rating)}</TableCell>
                      <TableCell>
                        <p className="max-w-md truncate">
                          {testimonial.testimonialText}
                        </p>
                      </TableCell>
                      <TableCell>
                        {testimonial.location || (
                          <span className="text-muted-foreground">N/A</span>
                        )}
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleApproval(testimonial)}
                          disabled={togglingId === testimonial.id}
                          className="gap-1"
                        >
                          {testimonial.isApproved ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-green-600">Approved</span>
                            </>
                          ) : (
                            <>
                              <XCircle className="h-4 w-4 text-orange-600" />
                              <span className="text-orange-600">Pending</span>
                            </>
                          )}
                        </Button>
                      </TableCell>
                      <TableCell className="text-center">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleFeatured(testimonial)}
                          disabled={togglingId === testimonial.id}
                        >
                          {testimonial.isFeatured ? (
                            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                          ) : (
                            <StarOff className="h-4 w-4 text-muted-foreground" />
                          )}
                        </Button>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              router.push(`/admin/testimonials/${testimonial.id}`)
                            }
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(testimonial.id)}
                            disabled={deletingId === testimonial.id}
                          >
                            <Trash2 className="h-4 w-4 text-destructive" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
