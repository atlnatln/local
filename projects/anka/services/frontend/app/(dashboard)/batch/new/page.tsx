'use client';

import { FormEvent, useState } from 'react';

interface CreateBatchRequest {
  city: string;
  sector: string;
  filters: Record<string, any>;
  sort_rule_version: number;
}

export default function CreateBatchPage() {
  const [formData, setFormData] = useState<CreateBatchRequest>({
    city: '',
    sector: '',
    filters: {},
    sort_rule_version: 1,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch('/api/batches/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setSuccess(`Batch created: ${data.id}`);
        // Reset form
        setFormData({
          city: '',
          sector: '',
          filters: {},
          sort_rule_version: 1,
        });
        // Redirect after 2 seconds
        setTimeout(() => {
          window.location.href = `/batches/${data.id}`;
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create batch');
      }
    } catch (err) {
      setError('An error occurred');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Create New Batch</h2>

      <form onSubmit={handleSubmit}>
        <div>
          <label>City:</label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            required
            placeholder="e.g., Istanbul"
          />
        </div>

        <div>
          <label>Sector:</label>
          <input
            type="text"
            value={formData.sector}
            onChange={(e) => setFormData({ ...formData, sector: e.target.value })}
            required
            placeholder="e.g., Technology"
          />
        </div>

        <div>
          <label>Sort Rule Version:</label>
          <input
            type="number"
            value={formData.sort_rule_version}
            onChange={(e) => setFormData({ ...formData, sort_rule_version: parseInt(e.target.value) })}
            min="1"
          />
        </div>

        {error && <p style={{ color: 'red' }}>{error}</p>}
        {success && <p style={{ color: 'green' }}>{success}</p>}

        <button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Batch'}
        </button>
      </form>
    </div>
  );
}
