/**
 * TypeScript declarations for NextAuth.js
 * Extends default types to include custom properties
 */

import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  /**
   * Extended User type with admin properties and JWT tokens
   */
  interface User {
    id: string;
    email: string;
    name?: string | null;
    image?: string | null;
    isAdmin?: boolean;
    adminRole?: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
    accessToken?: string;
    refreshToken?: string;
  }

  /**
   * Extended Session type with access token
   */
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string | null;
      image?: string | null;
      isAdmin: boolean;
      adminRole: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
      accessToken?: string;
      refreshToken?: string;
    };
  }
}

declare module "next-auth/jwt" {
  /**
   * Extended JWT type with backend JWT tokens
   */
  interface JWT {
    id: string;
    isAdmin: boolean;
    adminRole: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
    accessToken?: string;
    refreshToken?: string;
    lastRefresh?: number;
  }
}
