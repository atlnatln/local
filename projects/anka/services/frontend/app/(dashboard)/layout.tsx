'use client'

import { ReactNode, useEffect, useRef, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { isAuthenticated, logout, getCurrentUser, User } from '@/lib/auth'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { ToastProvider } from '@/components/ToastProvider'

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Gösterge Paneli',
  '/batch/new': 'Yeni Batch Oluştur',
  '/exports': 'İndirilmişler',
  '/checkout': 'Kredi Satın Al',
  '/settings': 'Ayarlar',
}

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter()
  const pathname = usePathname()
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const userMenuRef = useRef<HTMLDivElement>(null)

  // Close user menu on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
    }
    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showUserMenu])

  useEffect(() => {
    async function checkAuth() {
      try {
        if (!isAuthenticated()) {
          router.push('/login')
          return
        }

        const currentUser = await getCurrentUser()
        setUser(currentUser)
      } catch {
        router.push('/login')
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [router])

  // Close sidebar on route change (mobile)
  useEffect(() => {
    setSidebarOpen(false)
  }, [pathname])

  const handleLogout = async () => {
    try {
      await logout()
      router.push('/login')
    } catch (error) {
      console.error('Logout error:', error)
      router.push('/login')
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 h-12 w-12 mb-4"></div>
          <p className="text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    )
  }

  return (
    <ToastProvider>
    <div className="flex min-h-screen bg-gray-50">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 flex flex-col
          transform transition-transform duration-200 ease-in-out
          lg:relative lg:translate-x-0 lg:z-auto
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between border-b border-gray-200 px-6">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">
            Anka
          </Link>
          {/* Close button (mobile only) */}
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-4">
          <NavLink href="/dashboard" label="Gösterge Paneli" />
          <NavLink href="/batch/new" label="Yeni Batch" />
          <NavLink href="/exports" label="İndirilmişler" />
          <NavLink href="/checkout" label="Kredi Satın Al" />
          <NavLink href="/settings" label="Ayarlar" />
        </nav>

        {/* User section */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full rounded-lg border border-gray-200 bg-white px-4 py-3 text-left text-sm font-medium text-gray-900 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <p className="font-medium truncate">{user?.username}</p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                </div>
                <svg className="h-4 w-4 text-gray-400 flex-shrink-0 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                </svg>
              </div>
            </button>

            {showUserMenu && (
              <div className="absolute bottom-full left-0 right-0 mb-2 rounded-lg border border-gray-200 bg-white shadow-lg z-10">
                <Link
                  href="/settings"
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-t-lg transition-colors"
                >
                  Ayarlar
                </Link>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-b-lg transition-colors"
                >
                  Çıkış Yap
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b border-gray-200 bg-white px-4 sm:px-8 py-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              {/* Hamburger button (mobile only) */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-1.5 -ml-1.5 rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              <h2 className="text-lg font-semibold text-gray-900 truncate">
                {PAGE_TITLES[pathname] ||
                  (pathname.startsWith('/batch/') && !pathname.endsWith('/new') ? 'Batch Detayı' : 'Kontrol Paneli')}
              </h2>
            </div>
            {user && (
              <div className="hidden sm:block text-sm text-gray-600 flex-shrink-0">
                Hoş geldiniz, <span className="font-medium">{user.first_name || user.username}</span>
              </div>
            )}
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 p-4 sm:p-6 lg:p-8">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </div>
      </main>
    </div>
    </ToastProvider>
  )
}

// Helper component for navigation links
function NavLink({ href, label }: { href: string; label: string }) {
  const pathname = usePathname()
  // Exact match for most routes; startsWith for nested pages like /batch/[id]
  const isActive = pathname === href || (href !== '/dashboard' && pathname.startsWith(href + '/'))
  return (
    <Link
      href={href}
      className={`block rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
        isActive
          ? 'bg-blue-50 text-blue-600 font-semibold'
          : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
      }`}
    >
      {label}
    </Link>
  )
}
