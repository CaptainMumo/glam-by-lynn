'use client'

import { Suspense, ReactNode, useState, useEffect, useRef } from 'react'
import { Loader2 } from 'lucide-react'

interface LazyLoadProps {
  children: ReactNode
  fallback?: ReactNode
  className?: string
}

/**
 * Lazy loading wrapper with suspense boundary
 * Use this to wrap components that should be code-split and loaded on demand
 */
export function LazyLoad({
  children,
  fallback,
  className = '',
}: LazyLoadProps) {
  const defaultFallback = (
    <div className={`flex items-center justify-center p-8 ${className}`}>
      <Loader2 className="h-8 w-8 animate-spin text-secondary" />
    </div>
  )

  return (
    <Suspense fallback={fallback || defaultFallback}>
      {children}
    </Suspense>
  )
}

/**
 * Intersection Observer based lazy loading for components
 * Loads component only when it enters viewport
 */
export function LazyLoadOnView({
  children,
  className = '',
  threshold = 0.1,
}: {
  children: ReactNode
  className?: string
  threshold?: number
}) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.disconnect()
        }
      },
      { threshold }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => observer.disconnect()
  }, [threshold])

  return (
    <div ref={ref} className={className}>
      {isVisible ? (
        children
      ) : (
        <div className="flex items-center justify-center p-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      )}
    </div>
  )
}
