/**
 * NextAuth.js configuration
 * Handles authentication with Google OAuth and session management
 */

import { NextAuthOptions, User as NextAuthUser } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import axios from "axios";
import { API_BASE_URL, API_ENDPOINTS } from "@/config/api";

/**
 * NextAuth configuration options
 */
export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
      authorization: {
        params: {
          prompt: "consent",
          access_type: "offline",
          response_type: "code",
        },
      },
    }),
  ],

  // Custom pages
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },

  // Session configuration
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  // JWT configuration
  jwt: {
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },

  // Callbacks for customizing behavior
  callbacks: {
    /**
     * Called when user signs in
     * Sends Google auth to backend to create/get user
     */
    async signIn({ user, account }) {
      if (!account) return false;

      try {
        // Send Google auth info to backend
        const response = await axios.post(
          `${API_BASE_URL}${API_ENDPOINTS.AUTH.GOOGLE_LOGIN}`,
          {
            email: user.email,
            googleId: account.providerAccountId,
            name: user.name,
            image: user.image,
          }
        );

        // Store backend user data
        if (response.data) {
          user.id = response.data.id;
          user.isAdmin = response.data.isAdmin;
          user.adminRole = response.data.adminRole;
        }

        return true;
      } catch (error) {
        console.error("Error signing in:", error);
        return false;
      }
    },

    /**
     * Called whenever a JWT is created or updated
     * Add custom claims to the token
     */
    async jwt({ token, user, trigger, session }) {
      // Initial sign in
      if (user) {
        token.id = user.id;
        token.isAdmin = user.isAdmin ?? false;
        token.adminRole = user.adminRole ?? null;
      }

      // Update session (when session is updated on client)
      if (trigger === "update" && session) {
        token.isAdmin = session.isAdmin;
        token.adminRole = session.adminRole;
      }

      // Refresh user data from backend periodically
      if (token.id && (!token.lastRefresh || Date.now() - (token.lastRefresh as number) > 60 * 60 * 1000)) {
        try {
          const response = await axios.get(`${API_BASE_URL}${API_ENDPOINTS.AUTH.ME}`, {
            headers: {
              Authorization: `Bearer ${token.id}`,
            },
          });

          if (response.data) {
            token.isAdmin = response.data.isAdmin;
            token.adminRole = response.data.adminRole;
            token.lastRefresh = Date.now();
          }
        } catch (error) {
          console.error("Error refreshing user data:", error);
        }
      }

      return token;
    },

    /**
     * Called whenever session is checked
     * Add custom properties to the session object
     */
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
        session.user.isAdmin = token.isAdmin as boolean;
        session.user.adminRole = token.adminRole as
          | "super_admin"
          | "product_manager"
          | "booking_manager"
          | "content_editor"
          | "artist"
          | null;
      }

      return session;
    },
  },

  // Events for logging
  events: {
    async signIn({ user }) {
      console.log(`User signed in: ${user.email}`);
    },
    async signOut({ token }) {
      console.log(`User signed out: ${token.email}`);
    },
  },

  // Enable debug messages in development
  debug: process.env.NODE_ENV === "development",
};

/**
 * Check if user is admin
 */
export function isAdmin(user: NextAuthUser | null | undefined): boolean {
  return user?.isAdmin === true;
}

/**
 * Check if user has specific admin role
 */
export function hasAdminRole(
  user: NextAuthUser | null | undefined,
  role: "super_admin" | "product_manager" | "booking_manager" | "content_editor" | "artist"
): boolean {
  return user?.isAdmin === true && user?.adminRole === role;
}

/**
 * Check if user is super admin
 */
export function isSuperAdmin(user: NextAuthUser | null | undefined): boolean {
  return hasAdminRole(user, "super_admin");
}
