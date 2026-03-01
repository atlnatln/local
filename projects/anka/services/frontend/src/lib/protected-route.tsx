/**
 * Higher Order Component for protecting routes that require authentication
 * Redirects to login if user is not authenticated
 */

'use client'

import { ReactNode, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { isAuthenticated } from '@/lib/auth'
import { fetchAPI } from '@/lib/api-client'

export function withAuth<P extends object>(
  WrappedComponent: React.ComponentType<P>
) {
  return function ProtectedComponent(props: P) {
    const router = useRouter()
    const [loading, setLoading] = useState(true)
    const [isAuth, setIsAuth] = useState(false)

    useEffect(() => {
      const checkAuth = async () => {
        try {
          // Fast path: local optimistic auth flag
          if (!isAuthenticated()) {
            // Fallback path: cookie-based session may still be valid
            await fetchAPI('/auth/me/')
          }
          setIsAuth(true)
        } catch {
          const currentPath =
            typeof window !== 'undefined'
              ? `${window.location.pathname}${window.location.search || ''}`
              : ''
          router.push(`/login${currentPath ? `?redirect=${encodeURIComponent(currentPath)}` : ''}`)
        } finally {
          setLoading(false)
        }
      }

      checkAuth()
    }, [router])

    if (loading) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 h-12 w-12 mb-4"></div>
            <p className="text-gray-600">Yükleniyor...</p>
          </div>
        </div>
      )
    }

    return isAuth ? <WrappedComponent {...props} /> : null
  }
}

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const router = useRouter()
  const [isAuth, setIsAuth] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (!isAuthenticated()) {
          await fetchAPI('/auth/me/')
        }
        setIsAuth(true)
      } catch {
        const currentPath =
          typeof window !== 'undefined'
            ? `${window.location.pathname}${window.location.search || ''}`
            : ''
        router.push(`/login${currentPath ? `?redirect=${encodeURIComponent(currentPath)}` : ''}`)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 h-12 w-12 mb-4"></div>
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    )
  }

  return isAuth ? children : null
}
