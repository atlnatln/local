'use client';

import { useEffect, useState } from 'react';

interface CreditBalance {
  balance: number;
  total_purchased: number;
  total_spent: number;
}

export default function DashboardPage() {
  const [credits, setCredits] = useState<CreditBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCreditBalance();
  }, []);

  async function fetchCreditBalance() {
    try {
      const response = await fetch('/api/credits/balance/', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setCredits(data);
      } else if (response.status === 401) {
        // Redirect to login
        window.location.href = '/login';
      } else {
        setError('Failed to fetch credit balance');
      }
    } catch (err) {
      setError('An error occurred');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: 'red' }}>{error}</p>;

  return (
    <div>
      <h2>Dashboard</h2>
      
      <section>
        <h3>Credit Balance</h3>
        {credits && (
          <div>
            <p>Current Balance: ${credits.balance.toFixed(2)}</p>
            <p>Total Purchased: ${credits.total_purchased.toFixed(2)}</p>
            <p>Total Spent: ${credits.total_spent.toFixed(2)}</p>
          </div>
        )}
        
        <button onClick={() => window.location.href = '/checkout'}>
          Purchase Credits
        </button>
      </section>

      <section>
        <h3>Recent Batches</h3>
        <p>Batch list would appear here</p>
        <a href="/batches">View All Batches</a>
      </section>

      <section>
        <h3>Recent Disputes</h3>
        <p>Dispute list would appear here</p>
        <a href="/disputes">View All Disputes</a>
      </section>
    </div>
  );
}
