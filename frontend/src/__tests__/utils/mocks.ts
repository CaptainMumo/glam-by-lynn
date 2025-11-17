/**
 * Mock utilities for testing
 * Provides mock data and functions for API calls, NextAuth, etc.
 */

// Mock Axios
export const mockAxios = {
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  patch: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
}

// Mock NextAuth hooks
export const mockUseSession = (session: any = null, status: 'loading' | 'authenticated' | 'unauthenticated' = 'unauthenticated') => {
  const { useSession } = require('next-auth/react')
  ;(useSession as jest.Mock).mockReturnValue({
    data: session,
    status,
    update: jest.fn(),
  })
}

export const mockSignIn = () => {
  const { signIn } = require('next-auth/react')
  return signIn as jest.Mock
}

export const mockSignOut = () => {
  const { signOut } = require('next-auth/react')
  return signOut as jest.Mock
}

// Mock Next.js Router
export const mockRouter = {
  push: jest.fn(),
  replace: jest.fn(),
  prefetch: jest.fn(),
  back: jest.fn(),
  pathname: '/',
  query: {},
  asPath: '/',
  events: {
    on: jest.fn(),
    off: jest.fn(),
    emit: jest.fn(),
  },
  beforePopState: jest.fn(),
  isFallback: false,
}

export const mockUseRouter = () => {
  const { useRouter } = require('next/navigation')
  ;(useRouter as jest.Mock).mockReturnValue(mockRouter)
  return mockRouter
}

export const mockUsePathname = (pathname: string = '/') => {
  const { usePathname } = require('next/navigation')
  ;(usePathname as jest.Mock).mockReturnValue(pathname)
}

export const mockUseSearchParams = (params: Record<string, string> = {}) => {
  const { useSearchParams } = require('next/navigation')
  const searchParams = new URLSearchParams(params)
  ;(useSearchParams as jest.Mock).mockReturnValue(searchParams)
}

// Reset all mocks
export const resetAllMocks = () => {
  jest.clearAllMocks()
  mockUseSession(null, 'unauthenticated')
  mockUseRouter()
  mockUsePathname('/')
  mockUseSearchParams()
}
