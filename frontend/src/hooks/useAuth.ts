/**
 * Authentication hooks
 * Custom hooks for accessing auth state and user info
 */

"use client";

import { useSession } from "next-auth/react";
import { User as NextAuthUser } from "next-auth";
import { isAdmin, hasAdminRole, isSuperAdmin } from "@/lib/auth";

/**
 * Hook to access current user and auth state
 */
export function useAuth() {
  const { data: session, status } = useSession();
  const loading = status === "loading";
  const authenticated = status === "authenticated";
  const user = session?.user as NextAuthUser | undefined;

  return {
    user: user ?? null,
    session,
    loading,
    authenticated,
    isAdmin: isAdmin(user),
    isSuperAdmin: isSuperAdmin(user),
  };
}

/**
 * Hook to check if user has specific admin role
 */
export function useAdminRole(
  role: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist"
) {
  const { user } = useAuth();
  return hasAdminRole(user as NextAuthUser | null | undefined, role);
}

/**
 * Hook to require authentication
 * Returns user or null if not authenticated
 */
export function useRequireAuth() {
  const { user, loading, authenticated } = useAuth();

  return {
    user: authenticated ? user : null,
    loading,
    authenticated,
  };
}

/**
 * Hook to require admin access
 * Returns whether user is admin
 */
export function useRequireAdmin() {
  const { user, loading, authenticated } = useAuth();
  const admin = isAdmin(user as NextAuthUser | null | undefined);

  return {
    user: admin ? user : null,
    loading,
    authenticated,
    isAdmin: admin,
  };
}
