"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useRequireAdmin } from "@/hooks/useAuth";
import axios from "axios";
import { z } from "zod";

const galleryPostSchema = z.object({
  mediaType: z.enum(["image", "video"]),
  mediaUrl: z.string().url("Invalid URL").max(500, "URL too long"),
  thumbnailUrl: z.string().url("Invalid URL").max(500, "URL too long").optional(),
  caption: z.string().max(1000, "Caption too long").optional(),
  tags: z.array(z.string()).optional(),
  sourceType: z.enum(["instagram", "tiktok", "original"]).optional(),
  isFeatured: z.boolean(),
  displayOrder: z.number().int().min(0, "Display order cannot be negative"),
});

type GalleryPostFormData = z.infer<typeof galleryPostSchema>;

const SOURCE_TYPES = [
  { value: "original", label: "Original", icon: "📷" },
  { value: "instagram", label: "Instagram", icon: "📸" },
  { value: "tiktok", label: "TikTok", icon: "🎵" },
];

export default function EditGalleryPost() {
  const router = useRouter();
  const params = useParams();
  const postId = params.id as string;
  const { user, loading: authLoading, isAdmin } = useRequireAdmin();

  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState<GalleryPostFormData>({
    mediaType: "image",
    mediaUrl: "",
    thumbnailUrl: "",
    caption: "",
    tags: [],
    sourceType: "original",
    isFeatured: false,
    displayOrder: 0,
  });

  const [tagInput, setTagInput] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    const fetchPost = async () => {
      if (!isAdmin || !postId) return;

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const session = await fetch("/api/auth/session").then(res => res.json());
        const token = session?.user?.accessToken;

        if (!token) {
          setLoadError("Authentication required");
          return;
        }

        const response = await axios.get(
          `${apiUrl}/api/admin/gallery/${postId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        const post = response.data;
        setFormData({
          mediaType: post.mediaType || "image",
          mediaUrl: post.mediaUrl || "",
          thumbnailUrl: post.thumbnailUrl || "",
          caption: post.caption || "",
          tags: post.tags || [],
          sourceType: post.sourceType || "original",
          isFeatured: post.isFeatured ?? false,
          displayOrder: post.displayOrder || 0,
        });
      } catch (err: any) {
        console.error("Error fetching post:", err);
        setLoadError(err.response?.data?.detail || "Failed to load gallery post");
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [isAdmin, postId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSubmitError("");

    try {
      galleryPostSchema.parse(formData);
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
      if (!submitData.thumbnailUrl) delete submitData.thumbnailUrl;
      if (!submitData.caption) delete submitData.caption;
      if (!submitData.sourceType) delete submitData.sourceType;
      if (!submitData.tags || submitData.tags.length === 0) delete submitData.tags;

      await axios.put(
        `${apiUrl}/api/admin/gallery/${postId}`,
        submitData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      router.push("/admin/gallery");
    } catch (err: any) {
      console.error("Error updating gallery post:", err);
      setSubmitError(err.response?.data?.detail || "Failed to update gallery post");
    } finally {
      setSubmitting(false);
    }
  };

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...(formData.tags || []), tagInput.trim()],
      });
      setTagInput("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags?.filter(tag => tag !== tagToRemove) || [],
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleAddTag();
    }
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
        <h1 className="text-3xl font-bold text-foreground">Edit Gallery Post</h1>
        <p className="text-muted-foreground mt-1">Update gallery post details</p>
      </div>

      {submitError && (
        <div className="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded">
          {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Media Type Selection */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Media Type</h2>
          <div className="flex gap-4">
            <label className={`flex-1 flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
              formData.mediaType === "image"
                ? "border-secondary bg-secondary/5"
                : "border-border hover:border-secondary/50"
            }`}>
              <input
                type="radio"
                name="mediaType"
                value="image"
                checked={formData.mediaType === "image"}
                onChange={(e) => setFormData({ ...formData, mediaType: e.target.value as any })}
                className="sr-only"
              />
              <div className="text-center">
                <div className="text-4xl mb-2">📷</div>
                <div className="font-medium text-foreground">Image</div>
              </div>
            </label>

            <label className={`flex-1 flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-colors ${
              formData.mediaType === "video"
                ? "border-secondary bg-secondary/5"
                : "border-border hover:border-secondary/50"
            }`}>
              <input
                type="radio"
                name="mediaType"
                value="video"
                checked={formData.mediaType === "video"}
                onChange={(e) => setFormData({ ...formData, mediaType: e.target.value as any })}
                className="sr-only"
              />
              <div className="text-center">
                <div className="text-4xl mb-2">🎥</div>
                <div className="font-medium text-foreground">Video</div>
              </div>
            </label>
          </div>
          {errors.mediaType && <p className="text-red-500 text-sm mt-2">{errors.mediaType}</p>}
        </div>

        {/* Media URLs */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Media URLs</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Media URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                value={formData.mediaUrl}
                onChange={(e) => setFormData({ ...formData, mediaUrl: e.target.value })}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="https://example.com/image.jpg"
              />
              {errors.mediaUrl && <p className="text-red-500 text-sm mt-1">{errors.mediaUrl}</p>}
              <p className="text-sm text-muted-foreground mt-1">
                Direct URL to the {formData.mediaType}
              </p>
            </div>

            {formData.mediaType === "video" && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Thumbnail URL
                </label>
                <input
                  type="url"
                  value={formData.thumbnailUrl}
                  onChange={(e) => setFormData({ ...formData, thumbnailUrl: e.target.value })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="https://example.com/thumbnail.jpg"
                />
                {errors.thumbnailUrl && <p className="text-red-500 text-sm mt-1">{errors.thumbnailUrl}</p>}
                <p className="text-sm text-muted-foreground mt-1">
                  Optional: Thumbnail image for video preview
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Media Preview */}
        {formData.mediaUrl && (
          <div className="bg-card border border-border rounded-lg p-6">
            <h2 className="text-xl font-semibold text-foreground mb-4">Preview</h2>
            <div className="aspect-square max-w-sm mx-auto rounded-lg overflow-hidden border border-border">
              {formData.mediaType === "image" ? (
                <img
                  src={formData.mediaUrl}
                  alt="Preview"
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = "/placeholder-image.png";
                  }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-muted">
                  <div className="text-center">
                    <svg className="w-16 h-16 text-muted-foreground mx-auto mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-sm text-muted-foreground">Video Preview</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Content Details */}
        <div className="bg-card border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">Content Details</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Caption
              </label>
              <textarea
                value={formData.caption}
                onChange={(e) => setFormData({ ...formData, caption: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                placeholder="Describe this photo or video..."
              />
              {errors.caption && <p className="text-red-500 text-sm mt-1">{errors.caption}</p>}
              <p className="text-sm text-muted-foreground mt-1">
                {formData.caption?.length || 0} / 1000 characters
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Tags
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="flex-1 px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                  placeholder="Enter a tag and press Enter"
                />
                <button
                  type="button"
                  onClick={handleAddTag}
                  className="px-4 py-2 bg-secondary text-foreground rounded-lg hover:bg-secondary/90"
                >
                  Add
                </button>
              </div>
              {formData.tags && formData.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {formData.tags.map((tag, index) => (
                    <span key={index} className="inline-flex items-center gap-1 px-3 py-1 bg-muted text-foreground rounded-full text-sm">
                      #{tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="text-muted-foreground hover:text-foreground"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Source Type
              </label>
              <div className="grid grid-cols-3 gap-3">
                {SOURCE_TYPES.map((source) => (
                  <label
                    key={source.value}
                    className={`flex items-center justify-center p-3 border-2 rounded-lg cursor-pointer transition-colors ${
                      formData.sourceType === source.value
                        ? "border-secondary bg-secondary/5"
                        : "border-border hover:border-secondary/50"
                    }`}
                  >
                    <input
                      type="radio"
                      name="sourceType"
                      value={source.value}
                      checked={formData.sourceType === source.value}
                      onChange={(e) => setFormData({ ...formData, sourceType: e.target.value as any })}
                      className="sr-only"
                    />
                    <div className="text-center">
                      <div className="text-2xl mb-1">{source.icon}</div>
                      <div className="text-sm font-medium text-foreground">{source.label}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Display Order
                </label>
                <input
                  type="number"
                  min="0"
                  value={formData.displayOrder}
                  onChange={(e) => setFormData({ ...formData, displayOrder: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-secondary"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Lower numbers appear first
                </p>
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="isFeatured"
                checked={formData.isFeatured}
                onChange={(e) => setFormData({ ...formData, isFeatured: e.target.checked })}
                className="h-4 w-4 text-secondary focus:ring-secondary border-border rounded"
              />
              <label htmlFor="isFeatured" className="ml-2 text-sm text-foreground">
                ⭐ Featured (display prominently on homepage)
              </label>
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => router.push("/admin/gallery")}
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
