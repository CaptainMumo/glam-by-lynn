import React from 'react'
import { siteConfig } from '@/lib/metadata'

interface OrganizationSchema {
  '@context': string
  '@type': string
  name: string
  description: string
  url: string
  logo: string
  image: string
  telephone: string
  address: {
    '@type': string
    addressLocality: string
    addressCountry: string
  }[]
  geo: {
    '@type': string
    latitude: string
    longitude: string
  }[]
  sameAs: string[]
  priceRange: string
}

export function OrganizationStructuredData() {
  const schema: OrganizationSchema = {
    '@context': 'https://schema.org',
    '@type': 'BeautySalon',
    name: siteConfig.name,
    description: siteConfig.description,
    url: siteConfig.url,
    logo: `${siteConfig.url}/logo.png`,
    image: `${siteConfig.url}${siteConfig.ogImage}`,
    telephone: '+254-XXX-XXXXXX', // TODO: Add actual phone number
    address: [
      {
        '@type': 'PostalAddress',
        addressLocality: 'Nairobi',
        addressCountry: 'KE',
      },
      {
        '@type': 'PostalAddress',
        addressLocality: 'Kitui',
        addressCountry: 'KE',
      },
    ],
    geo: [
      {
        '@type': 'GeoCoordinates',
        latitude: '-1.2921', // Nairobi coordinates
        longitude: '36.8219',
      },
      {
        '@type': 'GeoCoordinates',
        latitude: '-1.3669', // Kitui coordinates
        longitude: '38.0106',
      },
    ],
    sameAs: [
      siteConfig.links.facebook,
      siteConfig.links.instagram,
      siteConfig.links.twitter,
    ],
    priceRange: 'KSh',
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}

interface ProductSchema {
  '@context': string
  '@type': string
  name: string
  description: string
  image: string
  offers: {
    '@type': string
    priceCurrency: string
    price: string
    availability: string
  }
  brand: {
    '@type': string
    name: string
  }
}

export function ProductStructuredData({
  name,
  description,
  image,
  price,
  availability = 'InStock',
}: {
  name: string
  description: string
  image: string
  price: number
  availability?: 'InStock' | 'OutOfStock' | 'PreOrder'
}) {
  const schema: ProductSchema = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name,
    description,
    image,
    offers: {
      '@type': 'Offer',
      priceCurrency: 'KES',
      price: price.toString(),
      availability: `https://schema.org/${availability}`,
    },
    brand: {
      '@type': 'Brand',
      name: siteConfig.name,
    },
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}

interface ServiceSchema {
  '@context': string
  '@type': string
  name: string
  description: string
  provider: {
    '@type': string
    name: string
  }
  areaServed: string[]
  serviceType: string
}

export function ServiceStructuredData({
  name,
  description,
  serviceType,
}: {
  name: string
  description: string
  serviceType: string
}) {
  const schema: ServiceSchema = {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name,
    description,
    provider: {
      '@type': 'Organization',
      name: siteConfig.name,
    },
    areaServed: ['Nairobi', 'Kitui'],
    serviceType,
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}

interface BreadcrumbSchema {
  '@context': string
  '@type': string
  itemListElement: {
    '@type': string
    position: number
    name: string
    item: string
  }[]
}

export function BreadcrumbStructuredData({
  items,
}: {
  items: { name: string; url: string }[]
}) {
  const schema: BreadcrumbSchema = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: item.name,
      item: `${siteConfig.url}${item.url}`,
    })),
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
  )
}
