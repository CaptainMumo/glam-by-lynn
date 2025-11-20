import { Metadata } from 'next'

export const siteConfig = {
  name: 'Glam by Lynn',
  description: 'Premier makeup artistry and beauty services in Nairobi and Kitui, Kenya. Professional makeup, beauty products, and 2026 vision for comprehensive salon, spa, and barbershop services.',
  url: process.env.NEXT_PUBLIC_SITE_URL || 'https://glambylynn.com',
  ogImage: '/og-image.jpg',
  links: {
    facebook: 'https://facebook.com/glambylynn',
    instagram: 'https://instagram.com/glambylynn',
    twitter: 'https://twitter.com/glambylynn',
  },
}

export function constructMetadata({
  title = siteConfig.name,
  description = siteConfig.description,
  image = siteConfig.ogImage,
  noIndex = false,
  ...props
}: {
  title?: string
  description?: string
  image?: string
  noIndex?: boolean
} & Metadata = {}): Metadata {
  return {
    title,
    description,
    keywords: [
      'makeup artist Kenya',
      'beauty services Nairobi',
      'makeup Kitui',
      'bridal makeup',
      'professional makeup',
      'beauty products',
      'salon services',
      'spa services',
      'barbershop Kenya',
      'mobile beauty services',
    ],
    authors: [
      {
        name: 'Glam by Lynn',
        url: siteConfig.url,
      },
    ],
    creator: 'Glam by Lynn',
    openGraph: {
      type: 'website',
      locale: 'en_KE',
      url: siteConfig.url,
      title,
      description,
      siteName: siteConfig.name,
      images: [
        {
          url: image,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [image],
      creator: '@glambylynn',
    },
    icons: {
      icon: '/favicon.ico',
      shortcut: '/favicon-16x16.png',
      apple: '/apple-touch-icon.png',
    },
    manifest: '/site.webmanifest',
    metadataBase: new URL(siteConfig.url),
    ...(!noIndex && {
      robots: {
        index: true,
        follow: true,
        googleBot: {
          index: true,
          follow: true,
          'max-video-preview': -1,
          'max-image-preview': 'large',
          'max-snippet': -1,
        },
      },
    }),
    ...(noIndex && {
      robots: {
        index: false,
        follow: false,
      },
    }),
    ...props,
  }
}
