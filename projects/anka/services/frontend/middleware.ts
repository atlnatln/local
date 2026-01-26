import { NextResponse } from 'next/server'

export function middleware() {
  // Since we use localStorage, auth checks happen on the client side
  // via isAuthenticated() function in lib/auth.ts
  // Middleware cannot access localStorage, so we allow all requests
  // and let client-side logic handle authentication
  return NextResponse.next()
}

export const config = {
  matcher: [
    // Match all paths except:
    // - api routes
    // - _next/static
    // - _next/image
    // - favicon.ico
    '/((?!_next/static|_next/image|favicon.ico|api/).*)',
  ],
}
