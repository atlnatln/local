'use client';

export default function DisputesPage() {
  return (
    <div>
      <h2>Disputes</h2>
      <p>File and track data accuracy disputes here.</p>
      <p>Disputes are automatically resolved based on configured rules.</p>
      <button onClick={() => window.location.href = '/disputes/new'}>
        File New Dispute
      </button>
    </div>
  );
}
