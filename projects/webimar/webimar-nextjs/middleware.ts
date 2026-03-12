import { NextRequest, NextResponse } from 'next/server';

const ROOT_PLACEHOLDER_SEGMENTS = new Set(['[yapi-turu]', '%5Byapi-turu%5D']);
const PLAN_PLACEHOLDER_SEGMENTS = new Set(['[planId]', '%5BplanId%5D']);
const IL_PLACEHOLDER_SEGMENTS = new Set(['[ilSlug]', '%5BilSlug%5D']);

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

function normalizePathname(pathname: string): string {
  return pathname.endsWith('/') && pathname !== '/' ? pathname.slice(0, -1) : pathname;
}

function getPathSegments(pathname: string): string[] {
  return normalizePathname(pathname)
    .split('/')
    .filter(Boolean);
}

function isPlaceholderSegment(segment: string, placeholders: Set<string>): boolean {
  const decodedSegment = decodeLegacySlug(segment);
  return placeholders.has(segment) || placeholders.has(decodedSegment);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const segments = getPathSegments(pathname);

  if (segments.length === 1 && isPlaceholderSegment(segments[0], ROOT_PLACEHOLDER_SEGMENTS)) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = '/';
    return NextResponse.redirect(redirectUrl, 308);
  }

  if (
    segments.length === 2 &&
    segments[0] === 'cevre-duzeni-planlari' &&
    isPlaceholderSegment(segments[1], PLAN_PLACEHOLDER_SEGMENTS)
  ) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = '/cevre-duzeni-planlari/';
    return NextResponse.redirect(redirectUrl, 308);
  }

  if (
    segments.length === 3 &&
    segments[0] === 'cevre-duzeni-planlari' &&
    segments[1] === 'il' &&
    isPlaceholderSegment(segments[2], IL_PLACEHOLDER_SEGMENTS)
  ) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = '/cevre-duzeni-planlari/';
    return NextResponse.redirect(redirectUrl, 308);
  }

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
  matcher: ['/:path*'],
};
