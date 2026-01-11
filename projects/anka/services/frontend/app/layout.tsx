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
    <html lang="tr">
      <body>
        {/* Session provider would go here for authentication context */}
        {children}
      </body>
    </html>
  );
}
