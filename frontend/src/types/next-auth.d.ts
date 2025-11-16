/**
 * TypeScript declarations for NextAuth.js
 * Extends default types to include custom properties
 */

import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  /**
   * Extended User type with admin properties
   */
  interface User {
    id: string;
    email: string;
    name?: string | null;
    image?: string | null;
    isAdmin?: boolean;
    adminRole?: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
  }

  /**
   * Extended Session type
   */
  interface Session {
    user: {
      id: string;
      email: string;
      name?: string | null;
      image?: string | null;
      isAdmin: boolean;
      adminRole: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
    };
  }
}

declare module "next-auth/jwt" {
  /**
   * Extended JWT type
   */
  interface JWT {
    id: string;
    isAdmin: boolean;
    adminRole: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist" | null;
    lastRefresh?: number;
  }
}
