"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useRequireAdmin } from "@/hooks/useAuth";
import axios from "axios";
import { z } from "zod";

const servicePackageSchema = z.object({
  package_type: z.enum(["bridal_large", "bridal_small", "bride_only", "regular", "classes"]),
  name: z.string().min(1, "Name is required").max(255, "Name too long"),
  description: z.string().optional(),
  base_bride_price: z.number().min(0, "Price must be non-negative").optional(),
  base_maid_price: z.number().min(0, "Price must be non-negative").optional(),
  base_mother_price: z.number().min(0, "Price must be non-negative").optional(),
  base_other_price: z.number().min(0, "Price must be non-negative").optional(),
  max_maids: z.number().int().min(1, "Max maids must be at least 1").optional(),
  min_maids: z.number().int().min(0, "Min maids cannot be negative"),
  includes_facial: z.boolean(),
  duration_minutes: z.number().int().min(1, "Duration must be positive").optional(),
  is_active: z.boolean(),
  display_order: z.number().int().min(0, "Display order cannot be negative"),
}).refine(
  (data) => {
    if (data.max_maids !== undefined && data.min_maids !== undefined) {
      return data.max_maids >= data.min_maids;
    }
    return true;
  },
  {
    message: "Max maids must be greater than or equal to min maids",
    path: ["max_maids"],
  }
);

type ServicePackageFormData = z.infer<typeof servicePackageSchema>;

const PACKAGE_TYPES = [
  { value: "bridal_large", label: "Large Bridal Party", description: "Large bridal party with multiple maids" },
  { value: "bridal_small", label: "Small Bridal Party", description: "Small bridal party with few maids" },
  { value: "bride_only", label: "Bride Only", description: "Bride makeup only" },
  { value: "regular", label: "Regular Makeup", description: "Regular makeup service" },
  { value: "classes", label: "Makeup Classes", description: "Makeup training classes" },
];

export default function EditServicePackage() {
  const router = useRouter();
  const params = useParams();
  const packageId = params.id as string;
  const { user, loading: authLoading, isAdmin } = useRequireAdmin();

  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState<ServicePackageFormData>({
    package_type: "bridal_large",
    name: "",
    description: "",
    base_bride_price: undefined,
    base_maid_price: undefined,
    base_mother_price: undefined,
    base_other_price: undefined,
    max_maids: undefined,
    min_maids: 0,
    includes_facial: false,
    duration_minutes: undefined,
    is_active: true,
    display_order: 0,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    const fetchPackage = async () => {
      if (!isAdmin || !packageId) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const session = await fetch("/api/auth/session").then(res => res.json());
        const token = session?.user?.accessToken;

        if (!token) {
          setLoadError("Authentication required");
          return;
        }

        const response = await axios.get(
          `${apiUrl}/api/admin/services/${packageId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const pkg = response.data;
        setFormData({
          package_type: pkg.package_type || "bridal_large",
          name: pkg.name || "",
          description: pkg.description || "",
          base_bride_price: pkg.base_bride_price || undefined,
          base_maid_price: pkg.base_maid_price || undefined,
          base_mother_price: pkg.base_mother_price || undefined,
          base_other_price: pkg.base_other_price || undefined,
          max_maids: pkg.max_maids || undefined,
          min_maids: pkg.min_maids || 0,
          includes_facial: pkg.includes_facial ?? false,
          duration_minutes: pkg.duration_minutes || undefined,
          is_active: pkg.is_active ?? true,
          display_order: pkg.display_order || 0,
        });
      } catch (err: any) {
        console.error("Error fetching package:", err);
        setLoadError(err.response?.data?.detail || "Failed to load service package");
      } finally {
        setLoading(false);
      }
    };

    fetchPackage();
  }, [isAdmin, packageId]);

  // Determine which fields are relevant based on package type
  const getRelevantFields = (packageType: string) => {
    switch (packageType) {
      case "bridal_large":
      case "bridal_small":
        return {
          showBridePrice: true,
          showMaidPrice: true,
          showMotherPrice: true,
          showOtherPrice: true,
          showMaidRange: true,
          showFacial: true,
        };
      case "bride_only":
        return {
          showBridePrice: true,
          showMaidPrice: false,
          showMotherPrice: true,
          showOtherPrice: false,
          showMaidRange: false,
          showFacial: true,
        };
      case "regular":
        return {
          showBridePrice: false,
          showMaidPrice: false,
          showMotherPrice: false,
          showOtherPrice: true,
          showMaidRange: false,
          showFacial: true,
        };
      case "classes":
        return {
          showBridePrice: false,
          showMaidPrice: false,
          showMotherPrice: false,
          showOtherPrice: true,
          showMaidRange: false,
          showFacial: false,
        };
      default:
        return {
          showBridePrice: true,
          showMaidPrice: true,
          showMotherPrice: true,
          showOtherPrice: true,
          showMaidRange: true,
          showFacial: true,
        };
    }
  };

  const relevantFields = getRelevantFields(formData.package_type);

  // Calculate estimated pricing preview
  const calculatePreview = () => {
    const { package_type, base_bride_price, base_maid_price, base_mother_price, base_other_price, max_maids, includes_facial } = formData;

    let total = 0;
    const breakdown: string[] = [];

    if (base_bride_price) {
      total += base_bride_price;
      breakdown.push(`Bride: KES ${base_bride_price.toLocaleString()}`);
    }

    if (base_mother_price) {
      total += base_mother_price;
      breakdown.push(`Mother: KES ${base_mother_price.toLocaleString()}`);
    }

    if (base_maid_price && max_maids) {
      const maidTotal = base_maid_price * max_maids;
      total += maidTotal;
      breakdown.push(`${max_maids} Maids: KES ${maidTotal.toLocaleString()}`);
    }

    if (base_other_price && !base_bride_price && !base_maid_price) {
      total += base_other_price;
      breakdown.push(`Base: KES ${base_other_price.toLocaleString()}`);
    }

    if (total > 0) {
      return {
        total,
        breakdown,
        hasData: true,
      };
    }

    return { total: 0, breakdown: [], hasData: false };
  };

  const preview = calculatePreview();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSubmitError("");

    try {
      servicePackageSchema.parse(formData);
    } catch (err) {
      if (err instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        err.issues.forEach((error: any) => {
          if (error.path) {
            newErrors[error.path.join(".")] = error.message;
          }
        });
        setErrors(newErrors);
        return;
      }
    }

    setSubmitting(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) {
        setSubmitError("Authentication required");
        return;
      }

      // Clean up data - remove undefined values
      const submitData: any = { ...formData };
      Object.keys(submitData).forEach(key => {
        if (submitData[key] === undefined || submitData[key] === "") {
          delete submitData[key];
        }
      });

      await axios.put(
        `${apiUrl}/api/admin/services/${packageId}`,
        submitData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      router.push("/admin/services");
    } catch (err: any) {
      console.error("Error updating package:", err);
      setSubmitError(err.response?.data?.detail || "Failed to update service package");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePackageTypeChange = (newType: string) => {
    // When changing package type, keep existing prices but user can clear them if needed
    setFormData({
      ...formData,
      package_type: newType as any,
    });
  };

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-secondary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return null;
  }

  if (loadError) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded">
          {loadError}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Edit Service Package</h1>
        <p className="text-muted-foreground mt-1">Update service package details and pricing</p>
      </div>

      {submitError && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Package Type Selection */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Package Type</h2>
          <div className="space-y-3">
            {PACKAGE_TYPES.map((type) => (
              <label
                key={type.value}
                className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.package_type === type.value
                    ? "border-secondary bg-secondary/5"
                    : "border-border hover:border-secondary/50"
                }`}
              >
                <input
                  type="radio"
                  name="package_type"
                  value={type.value}
                  checked={formData.package_type === type.value}
                  onChange={(e) => handlePackageTypeChange(e.target.value)}
                  className="mt-1 h-4 w-4 text-secondary focus:ring-secondary border-border"
                />
                <div className="ml-3 flex-1">
                  <div className="font-medium text-foreground">{type.label}</div>
                  <div className="text-sm text-muted-foreground">{type.description}</div>
                </div>
              </label>
            ))}
          </div>
          {errors.package_type && <p className="text-red-500 text-sm mt-2">{errors.package_type}</p>}
        </div>

        {/* Basic Information */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Basic Information</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Package Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="e.g., Premium Bridal Package"
              />
              {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="Describe what's included in this package..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.duration_minutes || ""}
                  onChange={(e) => setFormData({ ...formData, duration_minutes: e.target.value ? parseInt(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="e.g., 120"
                />
                {errors.duration_minutes && <p className="text-red-500 text-sm mt-1">{errors.duration_minutes}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Display Order
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.display_order}
                  onChange={(e) => setFormData({ ...formData, display_order: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Lower numbers appear first
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Pricing Configuration */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Pricing Configuration</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {relevantFields.showBridePrice && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Bride Price (KES)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.base_bride_price || ""}
                  onChange={(e) => setFormData({ ...formData, base_bride_price: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="0.00"
                />
                {errors.base_bride_price && <p className="text-red-500 text-sm mt-1">{errors.base_bride_price}</p>}
              </div>
            )}

            {relevantFields.showMaidPrice && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Maid Price (KES per person)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.base_maid_price || ""}
                  onChange={(e) => setFormData({ ...formData, base_maid_price: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="0.00"
                />
                {errors.base_maid_price && <p className="text-red-500 text-sm mt-1">{errors.base_maid_price}</p>}
              </div>
            )}

            {relevantFields.showMotherPrice && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Mother Price (KES)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.base_mother_price || ""}
                  onChange={(e) => setFormData({ ...formData, base_mother_price: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="0.00"
                />
                {errors.base_mother_price && <p className="text-red-500 text-sm mt-1">{errors.base_mother_price}</p>}
              </div>
            )}

            {relevantFields.showOtherPrice && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  {formData.package_type === "classes" ? "Class Price (KES)" : "Other Attendee Price (KES)"}
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.base_other_price || ""}
                  onChange={(e) => setFormData({ ...formData, base_other_price: e.target.value ? parseFloat(e.target.value) : undefined })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="0.00"
                />
                {errors.base_other_price && <p className="text-red-500 text-sm mt-1">{errors.base_other_price}</p>}
              </div>
            )}
          </div>

          {relevantFields.showMaidRange && (
            <div className="mt-4">
              <h3 className="text-sm font-semibold text-foreground mb-3">Maid Range Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Minimum Maids
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={formData.min_maids}
                    onChange={(e) => setFormData({ ...formData, min_maids: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  />
                  {errors.min_maids && <p className="text-red-500 text-sm mt-1">{errors.min_maids}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Maximum Maids
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.max_maids || ""}
                    onChange={(e) => setFormData({ ...formData, max_maids: e.target.value ? parseInt(e.target.value) : undefined })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                    placeholder="e.g., 10"
                  />
                  {errors.max_maids && <p className="text-red-500 text-sm mt-1">{errors.max_maids}</p>}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Additional Options */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Additional Options</h2>

          <div className="space-y-3">
            {relevantFields.showFacial && (
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="includes_facial"
                  checked={formData.includes_facial}
                  onChange={(e) => setFormData({ ...formData, includes_facial: e.target.checked })}
                  className="h-4 w-4 text-secondary focus:ring-secondary border-border rounded"
                />
                <label htmlFor="includes_facial" className="ml-2 text-sm text-foreground">
                  Includes facial treatment
                </label>
              </div>
            )}

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-secondary focus:ring-secondary border-border rounded"
              />
              <label htmlFor="is_active" className="ml-2 text-sm text-foreground">
                Active (visible to customers)
              </label>
            </div>
          </div>
        </div>

        {/* Pricing Preview */}
        {preview.hasData && (
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4">Pricing Preview</h2>
            <div className="space-y-2">
              {preview.breakdown.map((item, index) => (
                <div key={index} className="text-sm text-foreground/80">
                  {item}
                </div>
              ))}
              <div className="pt-2 mt-2 border-t border-purple-200 dark:border-purple-800">
                <div className="text-lg font-bold text-foreground">
                  Maximum Total: KES {preview.total.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  This is an estimated maximum based on configured prices
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.push("/admin/services")}
            className="px-6 py-2 border border-border rounded-lg text-foreground hover:bg-muted"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-secondary text-foreground rounded-lg hover:bg-secondary/90 disabled:opacity-50"
          >
            {submitting ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
