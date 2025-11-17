import React, { ReactElement } from 'react'
import { render, RenderOptions } from '@testing-library/react'
import { SessionProvider } from 'next-auth/react'

// Mock session data for testing
export const mockSession = {
  user: {
    id: '123',
    name: 'Test User',
    email: 'test@example.com',
    image: 'https://example.com/avatar.jpg',
    isAdmin: false,
    adminRole: null,
  },
  expires: '2099-12-31',
}

export const mockAdminSession = {
  user: {
    id: '456',
    name: 'Admin User',
    email: 'admin@example.com',
    image: 'https://example.com/admin-avatar.jpg',
    isAdmin: true,
    adminRole: 'super_admin' as const,
  },
  expires: '2099-12-31',
}

interface AllTheProvidersProps {
  children: React.ReactNode
  session?: any
}

function AllTheProviders({ children, session = null }: AllTheProvidersProps) {
  return (
    <SessionProvider session={session}>
      {children}
    </SessionProvider>
  )
}

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  session?: any
}

/**
 * Custom render function that includes all necessary providers
 *
 * @param ui - Component to render
 * @param options - Render options including optional session data
 * @returns Render result
 *
 * @example
 * ```tsx
 * import { renderWithProviders, mockSession } from '@/__tests__/utils/test-utils'
 *
 * renderWithProviders(<MyComponent />, { session: mockSession })
 * ```
 */
const customRender = (
  ui: ReactElement,
  { session, ...options }: CustomRenderOptions = {}
) => {
  return render(ui, {
    wrapper: (props) => <AllTheProviders session={session} {...props} />,
    ...options,
  })
}

// Re-export everything
export * from '@testing-library/react'
export { customRender as render }
