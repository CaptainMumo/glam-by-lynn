import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { render, mockSession, mockAdminSession } from '@/__tests__/utils/test-utils'
import { mockUseSession, mockSignOut } from '@/__tests__/utils/mocks'
import { Header } from '../Header'

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the Glam by Lynn logo', () => {
    mockUseSession(null, 'unauthenticated')
    render(<Header />)

    expect(screen.getByText('Glam by')).toBeInTheDocument()
    expect(screen.getByText('Lynn')).toBeInTheDocument()
  })

  it('displays navigation links', () => {
    mockUseSession(null, 'unauthenticated')
    render(<Header />)

    expect(screen.getByRole('link', { name: /home/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /services/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /products/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /gallery/i })).toBeInTheDocument()
  })

  it('shows Sign In button when not authenticated', () => {
    mockUseSession(null, 'unauthenticated')
    render(<Header />)

    const signInButton = screen.getByRole('link', { name: /sign in/i })
    expect(signInButton).toBeInTheDocument()
    expect(signInButton).toHaveAttribute('href', '/auth/signin')
  })

  it('shows user email and Sign Out button when authenticated', () => {
    mockUseSession(mockSession, 'authenticated')
    render(<Header />, { session: mockSession })

    expect(screen.getByText(mockSession.user.email)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign out/i })).toBeInTheDocument()
  })

  it('shows Admin badge and link for admin users', () => {
    mockUseSession(mockAdminSession, 'authenticated')
    render(<Header />, { session: mockAdminSession })

    // Check for admin badge (using getAllByText since there are multiple "Admin" texts)
    const adminTexts = screen.getAllByText('Admin')
    expect(adminTexts.length).toBeGreaterThan(0)

    // Check for admin link in navigation
    expect(screen.getByRole('link', { name: /admin/i })).toBeInTheDocument()
  })

  it('does not show Admin link for regular users', () => {
    mockUseSession(mockSession, 'authenticated')
    render(<Header />, { session: mockSession })

    expect(screen.queryByRole('link', { name: /^admin$/i })).not.toBeInTheDocument()
  })

  it('calls signOut when Sign Out button is clicked', async () => {
    const user = userEvent.setup()
    const signOutMock = mockSignOut()
    mockUseSession(mockSession, 'authenticated')

    render(<Header />, { session: mockSession })

    const signOutButton = screen.getByRole('button', { name: /sign out/i })
    await user.click(signOutButton)

    expect(signOutMock).toHaveBeenCalledTimes(1)
  })

  it('has correct logo link to homepage', () => {
    mockUseSession(null, 'unauthenticated')
    render(<Header />)

    const logoLink = screen.getByRole('link', { name: /glam by lynn/i })
    expect(logoLink).toHaveAttribute('href', '/')
  })
})
