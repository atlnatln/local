'use client';

import { useEffect, useState } from 'react';
import { fetchAPI } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

interface CreditPackage {
  id: string;
  organization: string;
  balance: string; // Decimal as string from API
  total_purchased: string;
  total_spent: string;
}

interface Batch {
  id: string;
  city: string;
  sector: string;
  status: string;
  record_count_estimate: number;
  created_at: string;
}


const getBatchStatusText = (status: string) => {
  switch (status) {
    case 'CREATED': return 'Oluşturuldu';
    case 'COLLECTING_IDS': return 'Havuz oluşturuluyor...';
    case 'FILTERING': return 'Sonuçlar doğrulanıyor...';
    case 'ENRICHING_CONTACTS': return 'İletişim bilgileri ekleniyor...';
    case 'READY': return 'Hazır';
    case 'PARTIAL': return 'Kısmen Tamamlandı';
    case 'FAILED': return 'Hata';
    case 'completed': return 'Tamamlandı'; // Legacy
    case 'processing': return 'İşleniyor'; // Legacy
    default: return status;
  }
};

const getBatchStatusColor = (status: string) => {
  switch (status) {
    case 'READY':
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'PARTIAL':
      return 'bg-amber-100 text-amber-800';
    case 'FAILED':
      return 'bg-red-100 text-red-800';
    case 'CREATED':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-blue-100 text-blue-800';
  }
};

export default function DashboardPage() {
  const [credits, setCredits] = useState<CreditPackage[]>([]);

  const [batches, setBatches] = useState<Batch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true);
        // Execute fetches in parallel
        const [creditsData, batchesData] = await Promise.all([
          fetchAPI<CreditPackage[]>('/credits/balance/'),
          fetchAPI<{ results: Batch[] }>('/batches/') // DRF pagination returns { count, results }
        ]);
        
        setCredits(creditsData || []);
        // Handle paginated response or direct array
        setBatches(batchesData.results || (Array.isArray(batchesData) ? batchesData : []));
      } catch (err: any) {
        console.error('Dashboard load error:', err);
        setError('Veriler yüklenirken bir hata oluştu.');
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 flex justify-center">
        <p>Yükleniyor...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 text-red-600 p-4 rounded-md">
          {error}
        </div>
      </div>
    );
  }

  // Calculate total balance across all orgs
  const totalBalance = credits.reduce((acc, curr) => acc + parseFloat(curr.balance), 0);

  return (
    <div className="p-6 space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam Kredi</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(totalBalance).toLocaleString('tr-TR')}</div>
            <p className="text-xs text-muted-foreground">
              Mevcut Bakiye
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Son Batchler</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{batches.length}</div>
            <p className="text-xs text-muted-foreground mr-2">
               İşlemde: {batches.filter(b => ['CREATED', 'COLLECTING_IDS', 'FILTERING', 'ENRICHING_CONTACTS', 'processing'].includes(b.status)).length}
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Son Aktiviteler</CardTitle>
          </CardHeader>
          <CardContent>
             {batches.length === 0 ? (
                <p className="text-sm text-gray-500">Henüz bir batch oluşturulmadı.</p>
             ) : (
                <div className="space-y-4">
                  {batches.slice(0, 5).map(batch => (
                    <Link key={batch.id} href={`/batch/${batch.id}`} className="block hover:bg-slate-50 transition-colors rounded p-2 -mx-2">
                        <div className="flex items-center justify-between border-b border-transparent pb-1">
                        <div>
                            <p className="font-medium">{batch.city} - {batch.sector}</p>
                            <p className="text-sm text-gray-500">{new Date(batch.created_at).toLocaleDateString('tr-TR')}</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className={`px-2 py-1 rounded text-xs ${getBatchStatusColor(batch.status)}`}>
                                {getBatchStatusText(batch.status)}
                            </span>
                        </div>
                        </div>
                    </Link>
                  ))}
                </div>
             )}
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Hızlı İşlemler</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
             <Link href="/batch/new">
               <Button className="w-full">Yeni Batch Oluştur</Button>
             </Link>
             <Link href="/checkout">
               <Button variant="outline" className="w-full">Kredi Yükle</Button>
             </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
