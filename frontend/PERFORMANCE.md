# Performance Optimization Guide

This document outlines the performance optimizations implemented in the Glam by Lynn frontend application.

## Image Optimization

### Next.js Image Component

All images use the Next.js `Image` component for automatic optimization:

```tsx
import Image from 'next/image'

<Image
  src="/path/to/image.jpg"
  alt="Description"
  width={800}
  height={600}
  priority={false} // Set to true for above-fold images
/>
```

### OptimizedImage Component

For enhanced image loading with error handling and transitions:

```tsx
import { OptimizedImage } from '@/components/OptimizedImage'

<OptimizedImage
  src="/path/to/image.jpg"
  alt="Description"
  width={800}
  height={600}
  fallbackSrc="/placeholder.jpg" // Optional fallback
  priority={false} // Above-fold images should set to true
/>
```

**Features:**
- Automatic lazy loading (except when `priority=true`)
- Blur placeholder while loading
- Smooth fade-in transition
- Error handling with fallback image
- WebP and AVIF format support

### Image Configuration

Images are optimized with the following settings in `next.config.ts`:

- **Formats**: WebP and AVIF for better compression
- **Device Sizes**: Responsive breakpoints for different screen sizes
- **Cache TTL**: 60 seconds minimum cache time
- **Remote Patterns**: Allow images from any HTTPS source

## Component Lazy Loading

### LazyLoad Component

Wrap components that should be code-split and loaded on demand:

```tsx
import { LazyLoad } from '@/components/LazyLoad'

<LazyLoad fallback={<CustomLoader />}>
  <HeavyComponent />
</LazyLoad>
```

### LazyLoadOnView Component

Load components only when they enter the viewport:

```tsx
import { LazyLoadOnView } from '@/components/LazyLoad'

<LazyLoadOnView threshold={0.1}>
  <ExpensiveComponent />
</LazyLoadOnView>
```

**Use cases:**
- Below-the-fold content
- Image galleries
- Comment sections
- Related products
- Footer content

## Code Splitting

### Dynamic Imports

For heavy components, use dynamic imports:

```tsx
import dynamic from 'next/dynamic'

const HeavyChart = dynamic(() => import('@/components/HeavyChart'), {
  loading: () => <Loader2 className="animate-spin" />,
  ssr: false, // Disable server-side rendering if needed
})
```

**When to use:**
- Charts and data visualizations
- Rich text editors
- Maps
- Video players
- Large UI libraries

## Route Prefetching

### Automatic Prefetching

Next.js automatically prefetches linked routes when using the `Link` component:

```tsx
import Link from 'next/link'

<Link href="/products" prefetch={true}>
  Products
</Link>
```

### Manual Prefetching

For programmatic prefetching:

```tsx
import { prefetchRoute, prefetchRoutes } from '@/lib/performance'

// Prefetch a single route
prefetchRoute('/products')

// Prefetch multiple routes
prefetchRoutes(['/products', '/services', '/about'])
```

**Best practices:**
- Prefetch on hover for navigation links
- Prefetch likely next steps in user flows
- Prefetch on idle time

## Performance Utilities

### Debounce

Limit function calls for search inputs, resize handlers, etc.:

```tsx
import { debounce } from '@/lib/performance'

const handleSearch = debounce((query: string) => {
  // Expensive search operation
}, 300)
```

### Throttle

Limit function execution rate for scroll handlers:

```tsx
import { throttle } from '@/lib/performance'

const handleScroll = throttle(() => {
  // Scroll handling logic
}, 100)
```

### Network-Aware Loading

Adjust loading behavior based on connection speed:

```tsx
import { isSlowConnection, getNetworkInfo } from '@/lib/performance'

if (isSlowConnection()) {
  // Load lighter version or defer non-critical content
}

const networkInfo = getNetworkInfo()
if (networkInfo?.saveData) {
  // Respect user's data saver preference
}
```

### Reduced Motion

Respect user's motion preferences:

```tsx
import { prefersReducedMotion } from '@/lib/performance'

if (!prefersReducedMotion()) {
  // Enable animations
}
```

## Best Practices

### Images

1. **Always use Next.js Image component** instead of `<img>` tags
2. **Set `priority={true}`** for above-the-fold images (LCP)
3. **Provide explicit dimensions** to prevent layout shift
4. **Use appropriate formats**: WebP/AVIF for modern browsers
5. **Optimize source images** before uploading (compress, resize)

### Components

1. **Code-split heavy components** using dynamic imports
2. **Lazy load below-the-fold content** with IntersectionObserver
3. **Use React.memo** for components with expensive renders
4. **Implement virtual scrolling** for long lists

### Data Fetching

1. **Use SWR or React Query** for data caching
2. **Prefetch data** for likely navigation paths
3. **Implement pagination** for large datasets
4. **Use suspense boundaries** for async components

### Build Optimization

1. **Enable SWC minification** (enabled in next.config.ts)
2. **Enable compression** (enabled in next.config.ts)
3. **Use React Strict Mode** (enabled in next.config.ts)
4. **Analyze bundle size** with `@next/bundle-analyzer`

## Performance Monitoring

### Lighthouse Scores

Target metrics:
- **Performance**: > 90
- **Accessibility**: > 90
- **Best Practices**: > 90
- **SEO**: > 90

### Core Web Vitals

Monitor these metrics:
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

### Testing

```bash
# Development build
npm run build
npm start

# Run Lighthouse in Chrome DevTools
# Or use CLI:
npx lighthouse http://localhost:3000 --view
```

## Optimization Checklist

- [ ] All images use Next.js Image component
- [ ] Above-fold images have `priority={true}`
- [ ] Heavy components use dynamic imports
- [ ] Below-fold content uses lazy loading
- [ ] Search inputs use debounce
- [ ] Scroll handlers use throttle
- [ ] Routes prefetch on hover
- [ ] Bundle size analyzed and optimized
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals pass
- [ ] Mobile performance tested
- [ ] Slow network performance tested

## Resources

- [Next.js Image Optimization](https://nextjs.org/docs/pages/building-your-application/optimizing/images)
- [Next.js Performance](https://nextjs.org/docs/pages/building-your-application/optimizing)
- [Web.dev Performance](https://web.dev/performance/)
- [Core Web Vitals](https://web.dev/vitals/)
