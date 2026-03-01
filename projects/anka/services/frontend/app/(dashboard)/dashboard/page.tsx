'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { fetchAPI } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
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

interface Export {
  id: string;
  batch: string;
  format: 'csv' | 'xlsx';
  status: string;
  total_rows: number;
  created_at: string;
}


const getBatchStatusText = (status: string) => {
  switch (status) {
    case 'CREATED': return 'Oluşturuldu';
    case 'COLLECTING_IDS': return 'Havuz oluşturuluyor...';
    case 'FILTERING': return 'Sonuçlar doğrulanıyor...';
    case 'ENRICHING_CONTACTS': return 'İletişim bilgileri ekleniyor...';
    case 'ENRICHING_EMAILS': return 'Email bilgileri aranıyor...';
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
  return (
    <Suspense fallback={
      <div className="p-8 flex justify-center">
        <p>Yükleniyor...</p>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const [credits, setCredits] = useState<CreditPackage[]>([]);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const [batches, setBatches] = useState<Batch[]>([]);
  const [totalBatchCount, setTotalBatchCount] = useState(0);
  const [recentExports, setRecentExports] = useState<Export[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    // Show payment success banner if redirected from checkout
    if (searchParams.get('success') === 'payment') {
      setPaymentSuccess(true);
      // Clean the URL without full reload — use Next.js router to keep state in sync
      router.replace('/dashboard', { scroll: false });
    }
  }, [searchParams, router]);

  useEffect(() => {
    let cancelled = false;
    let refreshTimer: ReturnType<typeof setTimeout>;

    async function loadDashboardData() {
      try {
        if (!cancelled) setLoading(prev => batches.length === 0 ? true : prev);
        // Execute fetches in parallel
        const [creditsRaw, batchesData, exportsData] = await Promise.all([
          fetchAPI<CreditPackage[] | CreditPackage>('/credits/balance/'),
          fetchAPI<{ count?: number; results: Batch[] }>('/batches/'),
          fetchAPI<{ results: Export[] }>('/exports/').catch(() => ({ results: [] })),
        ]);
        
        if (cancelled) return;
        // Backend returns CreditPackage[] array; guard defensively if single object
        const creditsData = Array.isArray(creditsRaw) ? creditsRaw : (creditsRaw ? [creditsRaw] : []);
        setCredits(creditsData);
        // Handle paginated response or direct array
        const items = batchesData.results || (Array.isArray(batchesData) ? batchesData : []);
        setBatches(items);
        setTotalBatchCount(batchesData.count ?? items.length);
        setRecentExports((exportsData.results || []).slice(0, 3));

        // Auto-refresh if any batch is still processing
        const hasProcessing = items.some((b: Batch) =>
          ['CREATED', 'COLLECTING_IDS', 'FILTERING', 'ENRICHING_CONTACTS', 'ENRICHING_EMAILS', 'processing'].includes(b.status)
        );
        if (hasProcessing && !cancelled) {
          refreshTimer = setTimeout(loadDashboardData, 5000);
        }
      } catch (err: any) {
        if (cancelled) return;
        console.error('Dashboard load error:', err);
        setError('Veriler yüklenirken bir hata oluştu.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadDashboardData();
    return () => { cancelled = true; clearTimeout(refreshTimer); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

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
  const totalBalance = credits.reduce((acc, curr) => {
    const val = parseFloat(curr.balance);
    return acc + (isNaN(val) ? 0 : val);
  }, 0);

  return (
    <div className="p-6 space-y-6">
      {paymentSuccess && (
        <Alert className="bg-green-50 border-green-200">
          <AlertDescription className="text-green-800 font-medium">
            Ödeme başarıyla tamamlandı! Kredileriniz hesabınıza yansıtılmıştır.
          </AlertDescription>
        </Alert>
      )}

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
            <div className="text-2xl font-bold">{totalBatchCount}</div>
            <p className="text-xs text-muted-foreground mr-2">
               İşlemde: {batches.filter(b => ['CREATED', 'COLLECTING_IDS', 'FILTERING', 'ENRICHING_CONTACTS', 'ENRICHING_EMAILS', 'processing'].includes(b.status)).length}
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
             {batches.length > 0 && totalBatchCount > 5 && (
                <p className="text-xs text-center text-gray-400 mt-4 pt-3 border-t">
                  Gösterilen: 5 / {totalBatchCount} batch. Tüm batch’lerinize Yeni Batch sayfasından ulaşabilirsiniz.
                </p>
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

      {/* Son İndirmeler */}
      {recentExports.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Son İndirmeler</CardTitle>
            <Link href="/exports" className="text-sm text-blue-600 hover:underline">Tümünü Gör</Link>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentExports.map(exp => {
                const batch = batches.find(b => b.id === exp.batch);
                return (
                  <div key={exp.id} className="flex items-center justify-between py-2 px-1 border-b last:border-0">
                    <div className="flex items-center gap-3">
                      <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold ${
                        exp.format === 'xlsx' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {exp.format.toUpperCase()}
                      </span>
                      <span className="text-sm font-medium">
                        {batch ? `${batch.city} – ${batch.sector}` : exp.batch.slice(0, 8)}
                      </span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        exp.status === 'completed' ? 'bg-green-100 text-green-700'
                          : exp.status === 'failed' ? 'bg-red-100 text-red-700'
                          : 'bg-blue-100 text-blue-700 animate-pulse'
                      }`}>
                        {exp.status === 'completed' ? 'Hazır' : exp.status === 'failed' ? 'Hata' : 'İşleniyor'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(exp.created_at).toLocaleDateString('tr-TR')}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
