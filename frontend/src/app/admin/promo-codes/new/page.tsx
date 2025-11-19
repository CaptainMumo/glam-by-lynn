"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
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
import { Sparkles } from "lucide-react";

export default function NewPromoCodePage() {
  const { isAdmin, loading: authLoading } = useRequireAdmin();
  const router = useRouter();

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

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateRandomCode = () => {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let code = "";
    for (let i = 0; i < 8; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setFormData((prev) => ({ ...prev, code }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
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

      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/promo-codes`,
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
      console.error("Error creating promo code:", err);
      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Failed to create promo code"
      );
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
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
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Add Promo Code</h1>
        <p className="text-muted-foreground">
          Create a new promotional discount code
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
              <div className="flex gap-2">
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
                <Button
                  type="button"
                  variant="outline"
                  onClick={generateRandomCode}
                >
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate
                </Button>
              </div>
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
            disabled={loading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create Promo Code"}
          </Button>
        </div>
      </form>
    </div>
  );
}
