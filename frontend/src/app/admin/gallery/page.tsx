"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { useRequireAdmin } from "@/hooks/useAuth";

interface GalleryPost {
  id: string;
  mediaType: "image" | "video";
  mediaUrl: string;
  thumbnailUrl?: string;
  caption?: string;
  tags?: string[];
  sourceType?: "instagram" | "tiktok" | "original";
  isFeatured: boolean;
  displayOrder: number;
  publishedAt: string;
}

interface GalleryListResponse {
  items: GalleryPost[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export default function GalleryManagement() {
  const router = useRouter();
  const { user, loading, isAdmin } = useRequireAdmin();

  const [posts, setPosts] = useState<GalleryPost[]>([]);
  const [totalPosts, setTotalPosts] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [mediaTypeFilter, setMediaTypeFilter] = useState<"all" | "image" | "video">("all");
  const [sourceFilter, setSourceFilter] = useState<"all" | "instagram" | "tiktok" | "original">("all");
  const [featuredFilter, setFeaturedFilter] = useState<"all" | "featured" | "not_featured">("all");
  const [loadingPosts, setLoadingPosts] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPosts = async () => {
      if (!isAdmin) return;

      setLoadingPosts(true);
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
        params.append("skip", ((currentPage - 1) * 20).toString());
        params.append("limit", "20");
        if (mediaTypeFilter !== "all") params.append("mediaType", mediaTypeFilter);
        if (sourceFilter !== "all") params.append("sourceType", sourceFilter);
        if (featuredFilter === "featured") params.append("isFeatured", "true");
        if (featuredFilter === "not_featured") params.append("isFeatured", "false");

        const response = await axios.get<GalleryListResponse>(
          `${apiUrl}/api/admin/gallery?${params}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        setPosts(response.data.items);
        setTotalPosts(response.data.total);
        setTotalPages(response.data.totalPages);
      } catch (err: any) {
        console.error("Error fetching gallery posts:", err);
        setError(err.response?.data?.detail || "Failed to load gallery posts");
      } finally {
        setLoadingPosts(false);
      }
    };

    fetchPosts();
  }, [isAdmin, currentPage, mediaTypeFilter, sourceFilter, featuredFilter]);

  const handleToggleFeatured = async (postId: string, currentStatus: boolean) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.put(
        `${apiUrl}/api/admin/gallery/${postId}`,
        { isFeatured: !currentStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Refresh posts
      window.location.reload();
    } catch (err) {
      console.error("Error toggling featured status:", err);
      alert("Failed to update featured status");
    }
  };

  const handleDeletePost = async (postId: string) => {
    if (!confirm("Are you sure you want to delete this gallery post? This action cannot be undone.")) {
      return;
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const session = await fetch("/api/auth/session").then(res => res.json());
      const token = session?.user?.accessToken;

      if (!token) return;

      await axios.delete(
        `${apiUrl}/api/admin/gallery/${postId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Refresh posts
      window.location.reload();
    } catch (err: any) {
      console.error("Error deleting post:", err);
      alert(err.response?.data?.detail || "Failed to delete post");
    }
  };

  const handleClearFilters = () => {
    setMediaTypeFilter("all");
    setSourceFilter("all");
    setFeaturedFilter("all");
    setCurrentPage(1);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
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
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Gallery Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage portfolio images and videos
          </p>
        </div>
        <button
          onClick={() => router.push("/admin/gallery/new")}
          className="bg-secondary hover:bg-secondary/90 text-foreground px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Upload Media
        </button>
      </div>

      {/* Filters */}
      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Media Type
            </label>
            <select
              value={mediaTypeFilter}
              onChange={(e) => setMediaTypeFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            >
              <option value="all">All Media</option>
              <option value="image">Images</option>
              <option value="video">Videos</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Source
            </label>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            >
              <option value="all">All Sources</option>
              <option value="instagram">Instagram</option>
              <option value="tiktok">TikTok</option>
              <option value="original">Original</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Featured
            </label>
            <select
              value={featuredFilter}
              onChange={(e) => setFeaturedFilter(e.target.value as any)}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
            >
              <option value="all">All Posts</option>
              <option value="featured">Featured</option>
              <option value="not_featured">Not Featured</option>
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

      {/* Gallery Grid */}
      <div className="bg-card border border-border rounded-lg overflow-hidden">
        {error && (
          <div className="bg-destructive/10 border-l-4 border-destructive text-destructive px-4 py-3">
            {error}
          </div>
        )}

        {loadingPosts ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-secondary"></div>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No gallery posts found</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-6">
              {posts.map((post) => (
                <div key={post.id} className="group relative bg-background border border-border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
                  {/* Media Preview */}
                  <div className="aspect-square relative">
                    {post.mediaType === "image" ? (
                      <img
                        src={post.thumbnailUrl || post.mediaUrl}
                        alt={post.caption || "Gallery image"}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = "/placeholder-image.png";
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-muted">
                        <svg className="w-12 h-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                    )}

                    {/* Featured Badge */}
                    {post.isFeatured && (
                      <div className="absolute top-2 left-2">
                        <span className="inline-flex px-2 py-1 text-xs font-medium rounded bg-yellow-100 text-yellow-800">
                          ⭐ Featured
                        </span>
                      </div>
                    )}

                    {/* Media Type Badge */}
                    <div className="absolute top-2 right-2">
                      <span className="inline-flex px-2 py-1 text-xs font-medium rounded bg-blue-100 text-blue-800">
                        {post.mediaType === "image" ? "📷" : "🎥"} {post.mediaType}
                      </span>
                    </div>
                  </div>

                  {/* Post Info */}
                  <div className="p-3">
                    {post.caption && (
                      <p className="text-sm text-foreground line-clamp-2 mb-2">
                        {post.caption}
                      </p>
                    )}

                    {post.tags && post.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {post.tags.slice(0, 3).map((tag, index) => (
                          <span key={index} className="text-xs px-2 py-0.5 rounded bg-muted text-muted-foreground">
                            #{tag}
                          </span>
                        ))}
                        {post.tags.length > 3 && (
                          <span className="text-xs text-muted-foreground">+{post.tags.length - 3}</span>
                        )}
                      </div>
                    )}

                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{post.sourceType || "original"}</span>
                      <span>{formatDate(post.publishedAt)}</span>
                    </div>

                    {/* Actions */}
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => router.push(`/admin/gallery/${post.id}`)}
                        className="flex-1 px-3 py-1.5 text-xs bg-secondary text-foreground rounded hover:bg-secondary/90"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleToggleFeatured(post.id, post.isFeatured)}
                        className="flex-1 px-3 py-1.5 text-xs border border-border rounded hover:bg-muted"
                      >
                        {post.isFeatured ? "Unfeature" : "Feature"}
                      </button>
                      <button
                        onClick={() => handleDeletePost(post.id)}
                        className="px-3 py-1.5 text-xs text-red-600 border border-red-300 rounded hover:bg-red-50"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            <div className="bg-muted px-6 py-4 border-t border-border flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Showing {posts.length} of {totalPosts} posts
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
