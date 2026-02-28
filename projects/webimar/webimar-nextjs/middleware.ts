import { NextRequest, NextResponse } from 'next/server';

function decodeLegacySlug(value: string): string {
  let decodedValue = value;

  for (let index = 0; index < 2; index += 1) {
    try {
      const nextValue = decodeURIComponent(decodedValue);
      if (nextValue === decodedValue) {
        break;
      }
      decodedValue = nextValue;
    } catch {
      break;
    }
  }

  return decodedValue;
}

function normalizeSlugValue(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/ı/g, 'i')
    .replace(/İ/g, 'i')
    .replace(/I/g, 'i')
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const match = pathname.match(/^\/cevre-duzeni-planlari\/il\/([^/]+)\/?$/);

  if (!match) {
    return NextResponse.next();
  }

  const rawSlug = match[1];
  const decodedSlug = decodeLegacySlug(rawSlug);
  const normalizedSlug = normalizeSlugValue(decodedSlug);

  if (!normalizedSlug) {
    return NextResponse.next();
  }

  if (rawSlug !== normalizedSlug || !pathname.endsWith('/')) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = `/cevre-duzeni-planlari/il/${normalizedSlug}/`;
    return NextResponse.redirect(redirectUrl, 308);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/cevre-duzeni-planlari/il/:path*'],
};
