"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useRequireAdmin } from "@/hooks/useAuth";
import axios from "axios";
import { z } from "zod";

const locationSchema = z.object({
  locationName: z.string().min(1, "Location name is required").max(255, "Name too long"),
  county: z.string().max(100, "County name too long").optional(),
  transportCost: z.number().min(0, "Transport cost must be non-negative"),
  isFree: z.boolean(),
  isActive: z.boolean(),
}).refine(
  (data) => {
    // If marked as free, transport cost should be 0
    if (data.isFree && data.transportCost > 0) {
      return false;
    }
    return true;
  },
  {
    message: "Free transport locations must have transport cost of 0",
    path: ["transportCost"],
  }
);

type LocationFormData = z.infer<typeof locationSchema>;

export default function NewLocation() {
  const router = useRouter();
  const { user, loading, isAdmin } = useRequireAdmin();

  const [formData, setFormData] = useState<LocationFormData>({
    locationName: "",
    county: "",
    transportCost: 0,
    isFree: false,
    isActive: true,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSubmitError("");

    try {
      locationSchema.parse(formData);
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

      const submitData: any = { ...formData };
      if (!submitData.county) delete submitData.county;

      await axios.post(
        `${apiUrl}/api/admin/locations`,
        submitData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      router.push("/admin/locations");
    } catch (err: any) {
      console.error("Error creating location:", err);
      setSubmitError(err.response?.data?.detail || "Failed to create location");
    } finally {
      setSubmitting(false);
    }
  };

  const handleFreeToggle = (isFree: boolean) => {
    setFormData({
      ...formData,
      isFree,
      transportCost: isFree ? 0 : formData.transportCost,
    });
  };

  if (loading) {
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

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Create Location</h1>
        <p className="text-muted-foreground mt-1">Add a new transport location</p>
      </div>

      {submitError && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Location Information</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Location Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.locationName}
                onChange={(e) => setFormData({ ...formData, locationName: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="e.g., Nairobi CBD, Kitui Town"
              />
              {errors.locationName && <p className="text-red-500 text-sm mt-1">{errors.locationName}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                County
              </label>
              <input
                type="text"
                value={formData.county}
                onChange={(e) => setFormData({ ...formData, county: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="e.g., Nairobi, Kitui"
              />
              {errors.county && <p className="text-red-500 text-sm mt-1">{errors.county}</p>}
              <p className="text-sm text-muted-foreground mt-1">
                Optional: Specify the county or region
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Transport Cost (KES)
              </label>
              <input
                type="number"
                min="0"
                step="0.01"
                value={formData.transportCost}
                onChange={(e) => setFormData({ ...formData, transportCost: parseFloat(e.target.value) || 0 })}
                disabled={formData.isFree}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="0.00"
              />
              {errors.transportCost && <p className="text-red-500 text-sm mt-1">{errors.transportCost}</p>}
              <p className="text-sm text-muted-foreground mt-1">
                Cost for transport to this location
              </p>
            </div>

            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  type="checkbox"
                  id="isFree"
                  checked={formData.isFree}
                  onChange={(e) => handleFreeToggle(e.target.checked)}
                  className="h-4 w-4 text-secondary focus:ring-secondary border-border rounded"
                />
              </div>
              <div className="ml-3">
                <label htmlFor="isFree" className="text-sm font-medium text-foreground">
                  Free Transport Location
                </label>
                <p className="text-sm text-muted-foreground">
                  Mark this location as free (transport cost will be set to 0)
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                  className="h-4 w-4 text-secondary focus:ring-secondary border-border rounded"
                />
              </div>
              <div className="ml-3">
                <label htmlFor="isActive" className="text-sm font-medium text-foreground">
                  Active
                </label>
                <p className="text-sm text-muted-foreground">
                  Location will be visible to customers when booking
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Location Preview</h2>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-foreground/80">Location:</span>
              <span className="font-medium text-foreground">{formData.locationName || "Not set"}</span>
            </div>
            {formData.county && (
              <div className="flex justify-between text-sm">
                <span className="text-foreground/80">County:</span>
                <span className="font-medium text-foreground">{formData.county}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span className="text-foreground/80">Transport Cost:</span>
              <span className="font-medium text-foreground">
                {formData.isFree ? (
                  <span className="text-green-600">FREE</span>
                ) : (
                  `KES ${formData.transportCost.toLocaleString()}`
                )}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-foreground/80">Status:</span>
              <span className={`font-medium ${formData.isActive ? "text-green-600" : "text-gray-600"}`}>
                {formData.isActive ? "Active" : "Inactive"}
              </span>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.push("/admin/locations")}
            className="px-6 py-2 border border-border rounded-lg text-foreground hover:bg-muted"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-secondary text-foreground rounded-lg hover:bg-secondary/90 disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Create Location"}
          </button>
        </div>
      </form>
    </div>
  );
}
