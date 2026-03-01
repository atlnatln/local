import { NextRequest, NextResponse } from 'next/server'

// Next.js 16: renamed from middleware to proxy (nodejs runtime, not edge)
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/', '/api']
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route + '/')
  )

  // Static and API routes
  if (pathname.startsWith('/_next/') || 
      pathname.startsWith('/api/') || 
      pathname === '/favicon.ico') {
    return NextResponse.next()
  }

  // For protected routes, redirect to login if not authenticated
  if (!isPublicRoute) {
    // Check for the token cookie
    const accessToken = request.cookies.get('anka_access_token')
    
    if (!accessToken) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Match all paths except static files and API routes
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
