import './globals.css'

export const metadata = {
  title: 'Anka Platform - B2B Data Utility',
  description: 'Deterministic batch processing for B2B data retrieval',
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
