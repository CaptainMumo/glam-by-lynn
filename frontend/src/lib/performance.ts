/**
 * Performance optimization utilities
 */

/**
 * Prefetch a route for faster navigation
 * @param href - The route to prefetch
 */
export function prefetchRoute(href: string) {
  if (typeof window === 'undefined') return

  const link = document.createElement('link')
  link.rel = 'prefetch'
  link.href = href
  link.as = 'document'
  document.head.appendChild(link)
}

/**
 * Prefetch multiple routes
 * @param routes - Array of routes to prefetch
 */
export function prefetchRoutes(routes: string[]) {
  routes.forEach((route) => prefetchRoute(route))
}

/**
 * Debounce function for performance optimization
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Throttle function for performance optimization
 * @param func - Function to throttle
 * @param limit - Time limit in milliseconds
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean = false

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func(...args)
      inThrottle = true
      setTimeout(() => (inThrottle = false), limit)
    }
  }
}

/**
 * Check if the device prefers reduced motion
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Get network information if available
 */
export function getNetworkInfo() {
  if (typeof navigator === 'undefined' || !('connection' in navigator)) {
    return null
  }

  const connection = (navigator as any).connection
  return {
    effectiveType: connection.effectiveType,
    downlink: connection.downlink,
    rtt: connection.rtt,
    saveData: connection.saveData,
  }
}

/**
 * Check if device is on a slow connection
 */
export function isSlowConnection(): boolean {
  const networkInfo = getNetworkInfo()
  if (!networkInfo) return false

  return (
    networkInfo.saveData ||
    networkInfo.effectiveType === 'slow-2g' ||
    networkInfo.effectiveType === '2g' ||
    networkInfo.effectiveType === '3g'
  )
}

/**
 * Lazy load a module with retry logic
 * @param importFunc - Dynamic import function
 * @param retries - Number of retries
 */
export async function lazyLoadWithRetry<T>(
  importFunc: () => Promise<T>,
  retries: number = 3
): Promise<T> {
  try {
    return await importFunc()
  } catch (error) {
    if (retries === 0) throw error
    await new Promise((resolve) => setTimeout(resolve, 1000))
    return lazyLoadWithRetry(importFunc, retries - 1)
  }
}
