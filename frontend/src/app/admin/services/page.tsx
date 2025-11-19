"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { useRequireAdmin } from "@/hooks/useAuth";

interface ServicePackage {
  id: string;
  package_type: string;
  name: string;
  description?: string;
  base_bride_price?: number;
  base_maid_price?: number;
  base_mother_price?: number;
  base_other_price?: number;
  max_maids?: number;
  min_maids: number;
  includes_facial: boolean;
  duration_minutes?: number;
  is_active: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
}

interface PackageListResponse {
  items: ServicePackage[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const PACKAGE_TYPES = [
  { value: "bridal_large", label: "Large Bridal Party" },
  { value: "bridal_small", label: "Small Bridal Party" },
  { value: "bride_only", label: "Bride Only" },
  { value: "regular", label: "Regular Makeup" },
  { value: "classes", label: "Makeup Classes" },
];

export default function ServicePackagesManagement() {
  const router = useRouter();
  const { user, loading, isAdmin } = useRequireAdmin();

  const [packages, setPackages] = useState<ServicePackage[]>([]);
  const [totalPackages, setTotalPackages] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [packageTypeFilter, setPackageTypeFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "inactive">("all");
  const [loadingPackages, setLoadingPackages] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPackages = async () => {
      if (!isAdmin) return;

      setLoadingPackages(true);
      setError("");

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const session = await fetch("/api/auth/session").then(res => res.json());
        const token = session?.user?.accessToken;

        if (!token) {
          setError("Authentication required");
          return;
        }

        const params = new URLSearchParams();
        params.append("page", currentPage.toString());
        params.append("page_size", "20");
        if (search) params.append("search", search);
        if (packageTypeFilter) params.append("package_type", packageTypeFilter);
        if (statusFilter === "active") params.append("is_active", "true");
        if (statusFilter === "inactive") params.append("is_active", "false");

        const response = await axios.get<PackageListResponse>(
          `${apiUrl}/api/admin/services?${params}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        setPackages(response.data.items);
        setTotalPackages(response.data.total);
        setTotalPages(response.data.total_pages);
      } catch (err: any) {
        console.error("Error fetching packages:", err);
        setError(err.response?.data?.detail || "Failed to load service packages");
      } finally {
        setLoadingPackages(false);
      }
    };

    fetchPackages();
  }, [isAdmin, currentPage, search, packageTypeFilter, statusFilter]);

  const handleToggleActive = async (packageId: string, currentStatus: boolean) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.put(
        `${apiUrl}/api/admin/services/${packageId}`,
        { is_active: !currentStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Refresh packages
      window.location.reload();
    } catch (err) {
      console.error("Error toggling package status:", err);
      alert("Failed to update package status");
    }
  };

  const handleDeletePackage = async (packageId: string, name: string) => {
    if (!confirm(`Are you sure you want to delete "${name}"? This action cannot be undone if there are no associated bookings.`)) {
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.delete(
        `${apiUrl}/api/admin/services/${packageId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Refresh packages
      window.location.reload();
    } catch (err: any) {
      console.error("Error deleting package:", err);
      alert(err.response?.data?.detail || "Failed to delete package");
    }
  };

  const handleClearFilters = () => {
    setSearch("");
    setPackageTypeFilter("");
    setStatusFilter("all");
    setCurrentPage(1);
  };

  const getPackageTypeLabel = (type: string) => {
    return PACKAGE_TYPES.find(t => t.value === type)?.label || type;
  };

  const formatPrice = (price?: number) => {
    if (price === null || price === undefined) return "N/A";
    return `KES ${price.toLocaleString()}`;
  };

  const formatDuration = (minutes?: number) => {
    if (!minutes) return "N/A";
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0 && mins > 0) return `${hours}h ${mins}m`;
    if (hours > 0) return `${hours}h`;
    return `${mins}m`;
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Service Packages</h1>
          <p className="text-muted-foreground mt-1">
            Manage makeup service packages and pricing
          </p>
        </div>
        <button
          onClick={() => router.push("/admin/services/new")}
          className="bg-secondary hover:bg-secondary/90 text-foreground px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Add Package
        </button>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Search
            </label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search packages..."
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Package Type
            </label>
            <select
              value={packageTypeFilter}
              onChange={(e) => setPackageTypeFilter(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            >
              <option value="">All Types</option>
              {PACKAGE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleClearFilters}
              className="w-full px-4 py-2 border border-border rounded-lg text-foreground hover:bg-muted transition-colors"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Packages List */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {error && (
          <div className="bg-destructive/10 border-l-4 border-destructive text-destructive px-4 py-3">
            {error}
          </div>
        )}

        {loadingPackages ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
          </div>
        ) : packages.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No service packages found</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-muted border-b border-border">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">Package Name</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">Type</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">Pricing</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">Duration</th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-foreground">Status</th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {packages.map((pkg) => (
                    <tr key={pkg.id} className="hover:bg-muted/50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium text-foreground">{pkg.name}</div>
                          {pkg.description && (
                            <div className="text-sm text-muted-foreground line-clamp-1">
                              {pkg.description}
                            </div>
                          )}
                          {pkg.includes_facial && (
                            <span className="inline-flex mt-1 px-2 py-0.5 text-xs font-medium rounded bg-purple-100 text-purple-800">
                              Includes Facial
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-foreground">
                          {getPackageTypeLabel(pkg.package_type)}
                        </span>
                        {(pkg.max_maids || pkg.min_maids > 0) && (
                          <div className="text-xs text-muted-foreground mt-1">
                            Maids: {pkg.min_maids}-{pkg.max_maids || "∞"}
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm space-y-0.5">
                          {pkg.base_bride_price !== null && pkg.base_bride_price !== undefined && (
                            <div className="text-foreground">
                              Bride: {formatPrice(pkg.base_bride_price)}
                            </div>
                          )}
                          {pkg.base_maid_price !== null && pkg.base_maid_price !== undefined && (
                            <div className="text-muted-foreground">
                              Maid: {formatPrice(pkg.base_maid_price)}
                            </div>
                          )}
                          {pkg.base_mother_price !== null && pkg.base_mother_price !== undefined && (
                            <div className="text-muted-foreground">
                              Mother: {formatPrice(pkg.base_mother_price)}
                            </div>
                          )}
                          {pkg.base_other_price !== null && pkg.base_other_price !== undefined && (
                            <div className="text-muted-foreground">
                              Other: {formatPrice(pkg.base_other_price)}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-foreground">
                          {formatDuration(pkg.duration_minutes)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-medium rounded ${
                            pkg.is_active
                              ? "bg-green-100 text-green-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {pkg.is_active ? "Active" : "Inactive"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => router.push(`/admin/services/${pkg.id}`)}
                            className="text-secondary hover:text-secondary/80 text-sm"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleToggleActive(pkg.id, pkg.is_active)}
                            className="text-foreground hover:text-foreground/80 text-sm"
                          >
                            {pkg.is_active ? "Deactivate" : "Activate"}
                          </button>
                          <button
                            onClick={() => handleDeletePackage(pkg.id, pkg.name)}
                            className="text-red-600 hover:text-red-800 text-sm"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="bg-muted px-6 py-4 border-t border-border flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {packages.length} of {totalPackages} packages
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 border border-border rounded text-sm text-foreground hover:bg-background disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <span className="px-3 py-1 text-sm text-foreground">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 border border-border rounded text-sm text-foreground hover:bg-background disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
