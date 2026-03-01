import './globals.css'
import type { Viewport } from 'next'

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  viewportFit: 'cover',
  themeColor: '#0066cc',
};

export const metadata = {
  title: 'Anka Platform - B2B Data Utility',
  description: 'Deterministic batch processing for B2B data retrieval',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Anka Data',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="tr" data-scroll-behavior="smooth">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
