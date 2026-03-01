/**
 * Next.js 16 Proxy (Middleware) — sunucu tarafı kimlik doğrulama
 *
 * Next.js 16'dan itibaren sunucu tarafı middleware dosyasının adı
 * `proxy.ts` olmalıdır (eski `middleware.ts` → `proxy.ts` olarak yeniden adlandırıldı).
 *
 * HttpOnly cookie'deki `anka_access_token` değerini kontrol eder:
 * - Korumalı sayfalarda: cookie yoksa `/login?redirect=<mevcut-sayfa>` yönlendir.
 * - Public sayfalarda (/login, /): giriş yapmış kullanıcı gelirse `/dashboard`'a yönlendir.
 */
import { NextRequest, NextResponse } from 'next/server'

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Statik dosyalar ve API proxy route'ları için geç
  if (
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname === '/favicon.ico'
  ) {
    return NextResponse.next()
  }

  // Kimlik doğrulama gerektirmeyen sayfalar
  const publicRoutes = ['/login', '/']
  const isPublicRoute = publicRoutes.some(
    (route) => pathname === route || pathname.startsWith(route + '/')
  )

  const accessToken = request.cookies.get('anka_access_token')

  // Zaten giriş yapmış kullanıcı login / landing sayfasına gelirse dashboard'a yönlendir
  if (isPublicRoute && accessToken) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  // Korumalı sayfalara cookie'siz erişim → login'e yönlendir
  if (!isPublicRoute && !accessToken) {
    const loginUrl = new URL('/login', request.url)
    const redirectTarget = `${pathname}${request.nextUrl.search || ''}`
    loginUrl.searchParams.set('redirect', redirectTarget)
    return NextResponse.redirect(loginUrl)
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    // Tüm yollar; statik dosyalar hariç
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}

