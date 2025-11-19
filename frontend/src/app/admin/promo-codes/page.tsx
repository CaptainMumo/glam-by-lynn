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
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Pencil, Trash2, CheckCircle, XCircle, Clock, AlertCircle } from "lucide-react";

interface PromoCode {
  id: string;
  code: string;
  description?: string;
  discountType: "percentage" | "fixed";
  discountValue: number;
  minOrderAmount?: number;
  maxDiscountAmount?: number;
  usageLimit?: number;
  usageCount: number;
  validFrom?: string;
  validUntil?: string;
  isActive: boolean;
  isExpired: boolean;
  isUsageExhausted: boolean;
  createdAt: string;
  updatedAt: string;
}

interface PromoCodeListResponse {
  items: PromoCode[];
  total: number;
}

export default function PromoCodesPage() {
  const { isAdmin, loading: authLoading } = useRequireAdmin();
  const router = useRouter();
  const [promoCodes, setPromoCodes] = useState<PromoCode[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Filters
  const [activeFilter, setActiveFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchPromoCodes = async () => {
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

      if (activeFilter !== "all") {
        params.append("isActive", activeFilter);
      }

      if (searchTerm) {
        params.append("search", searchTerm);
      }

      const response = await axios.get<PromoCodeListResponse>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/promo-codes?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setPromoCodes(response.data.items);
      setTotal(response.data.total);
    } catch (err: any) {
      console.error("Error fetching promo codes:", err);
      setError(err.response?.data?.detail || "Failed to load promo codes");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPromoCodes();
  }, [isAdmin, activeFilter, searchTerm]);

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this promo code?")) {
      return;
    }

    try {
      setDeletingId(id);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/promo-codes/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      await fetchPromoCodes();
    } catch (err: any) {
      console.error("Error deleting promo code:", err);
      alert(err.response?.data?.detail || "Failed to delete promo code");
    } finally {
      setDeletingId(null);
    }
  };

  const formatDiscount = (promoCode: PromoCode) => {
    if (promoCode.discountType === "percentage") {
      return `${promoCode.discountValue}%`;
    }
    return `KSh ${promoCode.discountValue}`;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusBadge = (promoCode: PromoCode) => {
    if (!promoCode.isActive) {
      return (
        <span className="inline-flex items-center gap-1 text-sm text-gray-500">
          <XCircle className="h-4 w-4" />
          Inactive
        </span>
      );
    }
    if (promoCode.isExpired) {
      return (
        <span className="inline-flex items-center gap-1 text-sm text-red-600">
          <Clock className="h-4 w-4" />
          Expired
        </span>
      );
    }
    if (promoCode.isUsageExhausted) {
      return (
        <span className="inline-flex items-center gap-1 text-sm text-orange-600">
          <AlertCircle className="h-4 w-4" />
          Usage Exhausted
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-sm text-green-600">
        <CheckCircle className="h-4 w-4" />
        Active
      </span>
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
          <h1 className="text-3xl font-bold">Promo Codes</h1>
          <p className="text-muted-foreground">
            Manage promotional discount codes
          </p>
        </div>
        <Button onClick={() => router.push("/admin/promo-codes/new")}>
          Add Promo Code
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
                Status
              </label>
              <Select
                value={activeFilter}
                onValueChange={setActiveFilter}
              >
                <SelectTrigger>
                  <SelectValue placeholder="All promo codes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All promo codes</SelectItem>
                  <SelectItem value="true">Active only</SelectItem>
                  <SelectItem value="false">Inactive only</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Search
              </label>
              <Input
                placeholder="Search by code or description..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            {total} Promo Code{total !== 1 ? "s" : ""}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {promoCodes.length === 0 ? (
            <div className="py-8 text-center text-muted-foreground">
              No promo codes found. Create your first promo code to get
              started.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Discount</TableHead>
                    <TableHead>Usage</TableHead>
                    <TableHead>Valid Period</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {promoCodes.map((promoCode) => (
                    <TableRow key={promoCode.id}>
                      <TableCell>
                        <div>
                          <p className="font-mono font-bold">{promoCode.code}</p>
                          {promoCode.description && (
                            <p className="text-sm text-muted-foreground">
                              {promoCode.description}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{formatDiscount(promoCode)}</p>
                          {promoCode.minOrderAmount && (
                            <p className="text-sm text-muted-foreground">
                              Min: KSh {promoCode.minOrderAmount}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">
                            {promoCode.usageCount}
                            {promoCode.usageLimit && ` / ${promoCode.usageLimit}`}
                          </p>
                          {promoCode.usageLimit && (
                            <div className="mt-1 h-2 w-20 overflow-hidden rounded-full bg-gray-200">
                              <div
                                className="h-full bg-blue-600"
                                style={{
                                  width: `${Math.min(
                                    (promoCode.usageCount / promoCode.usageLimit) * 100,
                                    100
                                  )}%`,
                                }}
                              />
                            </div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <p>From: {formatDate(promoCode.validFrom)}</p>
                          <p>Until: {formatDate(promoCode.validUntil)}</p>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(promoCode)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() =>
                              router.push(`/admin/promo-codes/${promoCode.id}`)
                            }
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(promoCode.id)}
                            disabled={deletingId === promoCode.id}
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
