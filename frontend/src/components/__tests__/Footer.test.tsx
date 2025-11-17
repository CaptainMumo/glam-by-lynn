import { screen } from '@testing-library/react'
import { render } from '@/__tests__/utils/test-utils'
import { Footer } from '../Footer'

describe('Footer Component', () => {
  it('renders the Glam by Lynn brand name', () => {
    render(<Footer />)

    expect(screen.getByText('Glam by')).toBeInTheDocument()
    expect(screen.getByText('Lynn')).toBeInTheDocument()
  })

  it('displays the brand description', () => {
    render(<Footer />)

    expect(
      screen.getByText(/professional makeup services and premium beauty products/i)
    ).toBeInTheDocument()
  })

  it('renders Services section links', () => {
    render(<Footer />)

    expect(screen.getByRole('link', { name: /bridal makeup/i })).toHaveAttribute('href', '/services#bridal')
    expect(screen.getByRole('link', { name: /special events/i })).toHaveAttribute('href', '/services#events')
    expect(screen.getByRole('link', { name: /makeup classes/i })).toHaveAttribute('href', '/services#classes')
    expect(screen.getByRole('link', { name: /consultations/i })).toHaveAttribute('href', '/services#consultations')
  })

  it('renders Shop section links', () => {
    render(<Footer />)

    expect(screen.getByRole('link', { name: /all products/i })).toHaveAttribute('href', '/products')
    expect(screen.getByRole('link', { name: /^makeup$/i })).toHaveAttribute('href', '/products?category=makeup')
    expect(screen.getByRole('link', { name: /skincare/i })).toHaveAttribute('href', '/products?category=skincare')
    expect(screen.getByRole('link', { name: /tools & brushes/i })).toHaveAttribute('href', '/products?category=tools')
  })

  it('renders Company section links', () => {
    render(<Footer />)

    expect(screen.getByRole('link', { name: /about us/i })).toHaveAttribute('href', '/about')
    expect(screen.getByRole('link', { name: /gallery/i })).toHaveAttribute('href', '/gallery')
    expect(screen.getByRole('link', { name: /contact/i })).toHaveAttribute('href', '/contact')
    expect(screen.getByRole('link', { name: /^faq$/i })).toHaveAttribute('href', '/faq')
  })

  it('displays current year in copyright', () => {
    render(<Footer />)

    const currentYear = new Date().getFullYear()
    expect(screen.getByText(new RegExp(`© ${currentYear} Glam by Lynn`))).toBeInTheDocument()
  })

  it('renders legal links', () => {
    render(<Footer />)

    expect(screen.getByRole('link', { name: /privacy policy/i })).toHaveAttribute('href', '/privacy')
    expect(screen.getByRole('link', { name: /terms of service/i })).toHaveAttribute('href', '/terms')
  })
})
