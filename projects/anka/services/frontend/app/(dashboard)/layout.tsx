'use client';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      <header>
        <h1>Dashboard</h1>
        <nav>
          <a href="/dashboard">Overview</a>
          <a href="/batches">Batches</a>
          <a href="/exports">Exports</a>
          <a href="/disputes">Disputes</a>
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}
