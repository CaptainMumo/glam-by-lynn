import { renderHook } from '@testing-library/react'
import { useAuth } from '../useAuth'
import { mockUseSession } from '@/__tests__/utils/mocks'
import { mockSession, mockAdminSession } from '@/__tests__/utils/test-utils'

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('returns unauthenticated state when no session', () => {
    mockUseSession(null, 'unauthenticated')

    const { result } = renderHook(() => useAuth())

    expect(result.current.authenticated).toBe(false)
    expect(result.current.user).toBeNull()
    expect(result.current.loading).toBe(false)
    expect(result.current.isAdmin).toBe(false)
    expect(result.current.isSuperAdmin).toBe(false)
  })

  it('returns loading state', () => {
    mockUseSession(null, 'loading')

    const { result } = renderHook(() => useAuth())

    expect(result.current.loading).toBe(true)
    expect(result.current.authenticated).toBe(false)
  })

  it('returns authenticated state for regular user', () => {
    mockUseSession(mockSession, 'authenticated')

    const { result } = renderHook(() => useAuth())

    expect(result.current.authenticated).toBe(true)
    expect(result.current.user).toEqual(mockSession.user)
    expect(result.current.loading).toBe(false)
    expect(result.current.isAdmin).toBe(false)
    expect(result.current.isSuperAdmin).toBe(false)
  })

  it('returns authenticated state for admin user', () => {
    mockUseSession(mockAdminSession, 'authenticated')

    const { result } = renderHook(() => useAuth())

    expect(result.current.authenticated).toBe(true)
    expect(result.current.user).toEqual(mockAdminSession.user)
    expect(result.current.loading).toBe(false)
    expect(result.current.isAdmin).toBe(true)
    expect(result.current.isSuperAdmin).toBe(true)
  })

  it('provides session object', () => {
    mockUseSession(mockSession, 'authenticated')

    const { result } = renderHook(() => useAuth())

    expect(result.current.session).toBeDefined()
  })
})
