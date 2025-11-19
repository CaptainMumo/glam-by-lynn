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

export default function EditPromoCodePage() {
  const { isAdmin, loading: authLoading } = useRequireAdmin();
  const router = useRouter();
  const params = useParams();
  const promoCodeId = params.id as string;

  const [formData, setFormData] = useState({
    code: "",
    description: "",
    discountType: "percentage" as "percentage" | "fixed",
    discountValue: "",
    minOrderAmount: "",
    maxDiscountAmount: "",
    usageLimit: "",
    validFrom: "",
    validUntil: "",
    isActive: true,
  });

  const [usageCount, setUsageCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isAdmin && promoCodeId) {
      fetchPromoCode();
    }
  }, [isAdmin, promoCodeId]);

  const fetchPromoCode = async () => {
    try {
      setLoading(true);

      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) {
        setError("Authentication required");
        return;
      }

      const response = await axios.get<PromoCode>(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/promo-codes/${promoCodeId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const promoCode = response.data;
      setUsageCount(promoCode.usageCount);

      // Format dates for datetime-local input
      const formatDateForInput = (dateString?: string) => {
        if (!dateString) return "";
        const date = new Date(dateString);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");
        return `${year}-${month}-${day}T${hours}:${minutes}`;
      };

      setFormData({
        code: promoCode.code,
        description: promoCode.description || "",
        discountType: promoCode.discountType,
        discountValue: promoCode.discountValue.toString(),
        minOrderAmount: promoCode.minOrderAmount?.toString() || "",
        maxDiscountAmount: promoCode.maxDiscountAmount?.toString() || "",
        usageLimit: promoCode.usageLimit?.toString() || "",
        validFrom: formatDateForInput(promoCode.validFrom),
        validUntil: formatDateForInput(promoCode.validUntil),
        isActive: promoCode.isActive,
      });
    } catch (err: any) {
      console.error("Error fetching promo code:", err);
      setError(err.response?.data?.detail || "Failed to load promo code");
    } finally {
      setLoading(false);
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
        code: formData.code,
        discountType: formData.discountType,
        discountValue: parseFloat(formData.discountValue),
        isActive: formData.isActive,
      };

      if (formData.description) {
        payload.description = formData.description;
      }

      if (formData.minOrderAmount) {
        payload.minOrderAmount = parseFloat(formData.minOrderAmount);
      }

      if (formData.maxDiscountAmount) {
        payload.maxDiscountAmount = parseFloat(formData.maxDiscountAmount);
      }

      if (formData.usageLimit) {
        payload.usageLimit = parseInt(formData.usageLimit);
      }

      if (formData.validFrom) {
        payload.validFrom = new Date(formData.validFrom).toISOString();
      }

      if (formData.validUntil) {
        payload.validUntil = new Date(formData.validUntil).toISOString();
      }

      await axios.put(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/promo-codes/${promoCodeId}`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      router.push("/admin/promo-codes");
    } catch (err: any) {
      console.error("Error updating promo code:", err);
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to update promo code"
      );
    } finally {
      setSaving(false);
    }
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

  if (error && !formData.code) {
    return (
      <div className="container mx-auto py-8">
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive">{error}</p>
            <Button
              className="mt-4"
              onClick={() => router.push("/admin/promo-codes")}
            >
              Back to Promo Codes
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Edit Promo Code</h1>
        <p className="text-muted-foreground">
          Update promo code information
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
            <CardTitle>Code Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="code">
                Promo Code <span className="text-destructive">*</span>
              </Label>
              <Input
                id="code"
                value={formData.code}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    code: e.target.value.toUpperCase(),
                  }))
                }
                placeholder="e.g., SUMMER2024"
                required
                className="font-mono"
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Letters, numbers, underscores, and hyphens only
              </p>
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Internal description of this promo code..."
                rows={3}
              />
            </div>

            <div>
              <Label>Usage Statistics</Label>
              <div className="rounded-md border p-4">
                <p className="text-sm text-muted-foreground">
                  This promo code has been used <strong>{usageCount}</strong> time{usageCount !== 1 ? "s" : ""}.
                </p>
                {formData.usageLimit && (
                  <div className="mt-2">
                    <div className="flex justify-between text-sm">
                      <span>Progress</span>
                      <span>
                        {usageCount} / {formData.usageLimit}
                      </span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-gray-200">
                      <div
                        className="h-full bg-blue-600"
                        style={{
                          width: `${Math.min(
                            (usageCount / parseInt(formData.usageLimit)) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Discount Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="discountType">
                Discount Type <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.discountType}
                onValueChange={(value: "percentage" | "fixed") =>
                  setFormData((prev) => ({ ...prev, discountType: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="percentage">Percentage (%)</SelectItem>
                  <SelectItem value="fixed">Fixed Amount (KSh)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="discountValue">
                Discount Value <span className="text-destructive">*</span>
              </Label>
              <Input
                id="discountValue"
                type="number"
                step="0.01"
                min="0"
                max={formData.discountType === "percentage" ? "100" : undefined}
                value={formData.discountValue}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    discountValue: e.target.value,
                  }))
                }
                placeholder={
                  formData.discountType === "percentage"
                    ? "e.g., 10 (for 10%)"
                    : "e.g., 500 (for KSh 500)"
                }
                required
              />
              <p className="mt-1 text-sm text-muted-foreground">
                {formData.discountType === "percentage"
                  ? "Enter percentage value (0-100)"
                  : "Enter fixed amount in KSh"}
              </p>
            </div>

            <div>
              <Label htmlFor="minOrderAmount">Minimum Order Amount (KSh)</Label>
              <Input
                id="minOrderAmount"
                type="number"
                step="0.01"
                min="0"
                value={formData.minOrderAmount}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    minOrderAmount: e.target.value,
                  }))
                }
                placeholder="Optional minimum order amount"
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Leave empty for no minimum
              </p>
            </div>

            <div>
              <Label htmlFor="maxDiscountAmount">Maximum Discount Amount (KSh)</Label>
              <Input
                id="maxDiscountAmount"
                type="number"
                step="0.01"
                min="0"
                value={formData.maxDiscountAmount}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    maxDiscountAmount: e.target.value,
                  }))
                }
                placeholder="Optional maximum discount cap"
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Leave empty for no maximum
              </p>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Usage & Validity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="usageLimit">Usage Limit</Label>
              <Input
                id="usageLimit"
                type="number"
                min="1"
                value={formData.usageLimit}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    usageLimit: e.target.value,
                  }))
                }
                placeholder="e.g., 100"
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Leave empty for unlimited usage
              </p>
            </div>

            <div>
              <Label htmlFor="validFrom">Valid From</Label>
              <Input
                id="validFrom"
                type="datetime-local"
                value={formData.validFrom}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    validFrom: e.target.value,
                  }))
                }
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Leave empty to start immediately
              </p>
            </div>

            <div>
              <Label htmlFor="validUntil">Valid Until</Label>
              <Input
                id="validUntil"
                type="datetime-local"
                value={formData.validUntil}
                onChange={(e) =>
                  setFormData((prev) => ({
                    ...prev,
                    validUntil: e.target.value,
                  }))
                }
              />
              <p className="mt-1 text-sm text-muted-foreground">
                Leave empty for no expiration
              </p>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="isActive">Active</Label>
                <p className="text-sm text-muted-foreground">
                  Enable or disable this promo code
                </p>
              </div>
              <Switch
                id="isActive"
                checked={formData.isActive}
                onCheckedChange={(checked: boolean) =>
                  setFormData((prev) => ({ ...prev, isActive: checked }))
                }
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push("/admin/promo-codes")}
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
