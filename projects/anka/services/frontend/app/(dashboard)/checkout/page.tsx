/**
 * Checkout Page - Credit Purchase with Iyzico Payment
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { cn } from '@/lib/utils';
import { fetchAPI } from '@/lib/api-client';

interface CreditPackage {
  id: string;
  name: string;
  credits: number;
  price: number;
  popular?: boolean;
  description: string;
  features: string[];
}

const CREDIT_PACKAGES: CreditPackage[] = [
  {
    id: 'starter',
    name: 'Başlangıç',
    credits: 1000,
    price: 99,
    description: '1.000 Kredi',
    features: [
      '7 gün geçerli',
      'Sınırsız batch',
      '24/7 destek',
      'Otomatik çözüm kuralları',
      'CSV ve Excel dışa aktarma',
    ],
  },
  {
    id: 'professional',
    name: 'Profesyonel',
    credits: 5000,
    price: 399,
    popular: true,
    description: '5.000 Kredi',
    features: [
      '7 gün geçerli',
      'Sınırsız batch',
      '24/7 destek',
      'Otomatik çözüm kuralları',
      'CSV ve Excel dışa aktarma',
      'Öncelikli destek',
    ],
  },
  {
    id: 'enterprise',
    name: 'Kurumsal',
    credits: 20000,
    price: 1299,
    description: '20.000 Kredi',
    features: [
      '7 gün geçerli',
      'Sınırsız batch',
      '24/7 destek',
      'Otomatik çözüm kuralları',
      'CSV ve Excel dışa aktarma',
      'Öncelikli destek',
      'Özel fatura',
      'Teknik danışma',
    ],
  },
];

interface FAQ {
  question: string;
  answer: string;
}

const FAQS: FAQ[] = [
  {
    question: 'Krediler ne kadar süre geçerli?',
    answer: 'Tüm krediler satın alımdan itibaren 7 gün boyunca geçerlidir. Bu süre zarfında kullanılmayan krediler otomatik olarak silinir.',
  },
  {
    question: 'Hangi ödeme yöntemlerini destekliyorsunuz?',
    answer: 'Tüm kredi kartları, mobil ödeme ve banka transferi gibi çeşitli ödeme yöntemlerini desteklemekteyiz.',
  },
  {
    question: 'Fatura alabilir miyim?',
    answer: 'Evet, tüm satın alımlar için fatura talep edebilirsiniz. Kurumsal paket başlıklarında otomatik fatura gönderilir.',
  },
  {
    question: 'Para iadesini nasıl talep edebilirim?',
    answer: 'Başarısız işlemler için otomatik para iadesi yapılır. 7 gün içinde kullanılmayan krediler için para iade talebinde bulunabilirsiniz.',
  },
];

export default function CheckoutPage() {
  const router = useRouter();
  const [selectedPackage, setSelectedPackage] = useState<CreditPackage | null>(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const [pendingPackage, setPendingPackage] = useState<CreditPackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [iyzicoReady, setIyzicoReady] = useState(false);
  const [currentBalance, setCurrentBalance] = useState<number | null>(null);

  // Load current credit balance
  useEffect(() => {
    async function loadBalance() {
      try {
        // Backend returns CreditPackage[] array (from ledger CreditBalanceView)
        const dataRaw = await fetchAPI<Array<{ balance: string }> | { balance: string }>('/credits/balance/');
        const dataArr = Array.isArray(dataRaw) ? dataRaw : (dataRaw ? [dataRaw] : []);
        const total = dataArr.reduce((sum, pkg) => {
          const val = parseFloat(pkg.balance || '0');
          return sum + (isNaN(val) ? 0 : val);
        }, 0);
        setCurrentBalance(total);
      } catch {
        // non-critical, just don't show balance
      }
    }
    loadBalance();
  }, []);

  // Initialize Iyzico on component mount
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://checkout.iyzipay.com/v1/iyzico.js';
    script.async = true;
    script.onload = () => setIyzicoReady(true);
    script.onerror = () => setError('Ödeme sistemi yüklenemedi. Sayfayı yenileyin.');
    document.body.appendChild(script);

    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script);
      }
    };
  }, []);

  const handlePackageSelect = async (pkg: CreditPackage) => {
    if (!iyzicoReady) {
      setError('Ödeme sistemi henüz yüklenmedi, lütfen birkaç saniye bekleyin.');
      return;
    }

    setSelectedPackage(pkg);
    setError('');
    setLoading(true);

    try {
      // Create payment intent on backend
      const response = await fetchAPI<any>('/payments/intents/', {
        method: 'POST',
        body: JSON.stringify({
          amount: pkg.price,
          credits: pkg.credits,
          package_type: pkg.id,
        }),
      });

      if (!response.checkoutFormContent || !response.token) {
        throw new Error('Failed to initialize payment form');
      }

      // Display Iyzico checkout form in modal/iframe
      const container = document.getElementById('iyzico-checkout');
      if (container) {
        container.innerHTML = response.checkoutFormContent;

        // Initialize Iyzico checkout — script already confirmed loaded
        if (typeof (window as any).Iyzipay !== 'undefined') {
          (window as any).Iyzipay.load({
            id: 'iyzico-checkout',
            token: response.token,
            locale: 'tr',
            onSuccess: (result: any) => handlePaymentSuccess(result, response.id),
            onError: (error: any) => handlePaymentError(error),
            onCancel: () => setLoading(false),
          });
        } else {
          throw new Error('Iyzipay modülü yüklenemedi');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ödeme başlatılırken hata oluştu');
      setLoading(false);
    }
  };

  const handlePaymentSuccess = async (result: any, intentId: string) => {
    try {
      setLoading(true);
      
      // Confirm payment on backend
      await fetchAPI(`/payments/intents/${intentId}/confirm/`, {
        method: 'POST',
        body: JSON.stringify({
          token: result.token,
          conversation_id: result.conversationId,
        }),
      });

      setSuccess(true);
      
      // Redirect to success page after 2 seconds
      setTimeout(() => {
        router.push('/dashboard?success=payment');
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ödeme onaylanırken hata oluştu');
      setLoading(false);
    }
  };

  const handlePaymentError = (error: any) => {
    setError(error?.message || 'Ödeme işleminde hata oluştu');
    setLoading(false);
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">✓ Ödeme Başarılı</CardTitle>
            <CardDescription>Kredileriniz hesabınıza eklendi</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-gray-600 mb-4">
              Dashboard'a yönlendiriliyorsunuz...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Kredi Satın Al</h1>
          <p className="mt-2 text-gray-600">
            Verilerinizi analiz etmek için kredi paketi seçin
          </p>
        </div>
        {currentBalance !== null && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg px-5 py-3 text-center">
            <p className="text-xs text-blue-500 font-medium uppercase tracking-wide">Mevcut Bakiye</p>
            <p className="text-2xl font-bold text-blue-700">{currentBalance.toLocaleString('tr-TR')}</p>
            <p className="text-xs text-blue-400">kredi</p>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertTitle>Hata</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Packages */}
      <div className="grid md:grid-cols-3 gap-6">
        {CREDIT_PACKAGES.map((pkg) => (
          <Card
            key={pkg.id}
            className={cn(
              'relative cursor-pointer transition-all hover:shadow-lg',
              selectedPackage?.id === pkg.id ? 'ring-2 ring-blue-500' : '',
              pkg.popular ? 'md:scale-105' : ''
            )}
            onClick={() => {
              if (!loading) {
                setPendingPackage(pkg);
                setShowConfirm(true);
              }
            }}
          >
            {pkg.popular && (
              <div className="absolute top-0 right-0 bg-yellow-500 text-white px-3 py-1 rounded-bl-lg text-sm font-semibold">
                Popüler
              </div>
            )}

            <CardHeader>
              <CardTitle className="text-2xl">{pkg.name}</CardTitle>
              <CardDescription>{pkg.description}</CardDescription>
            </CardHeader>

            <CardContent>
              <div className="mb-6">
                <div className="text-4xl font-bold text-gray-900 mb-2">
                  ₺{pkg.price}
                </div>
                <p className="text-sm text-gray-500">
                  {(pkg.price / pkg.credits).toFixed(4)}₺/kredi
                </p>
              </div>

              <ul className="space-y-2 mb-6">
                {pkg.features.map((feature, idx) => (
                  <li key={idx} className="text-sm text-gray-600 flex items-start">
                    <span className="text-blue-500 mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                disabled={loading}
                variant={selectedPackage?.id === pkg.id ? 'default' : 'outline'}
              >
                {loading && selectedPackage?.id === pkg.id
                  ? 'İşleniyor...'
                  : 'Satın Al'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Purchase Confirmation Dialog */}
      {showConfirm && pendingPackage && (
        <Card className="border-blue-200 bg-blue-50/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
              </span>
              Satın Alma Onayı
            </CardTitle>
            <CardDescription>Lütfen satın alma detaylarını kontrol edin.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg border border-gray-200 bg-white divide-y divide-gray-200 text-sm mb-4">
              <div className="flex justify-between px-4 py-3">
                <span className="text-gray-500">Paket</span>
                <span className="font-semibold text-gray-900">{pendingPackage.name}</span>
              </div>
              <div className="flex justify-between px-4 py-3">
                <span className="text-gray-500">Kredi Miktarı</span>
                <span className="font-semibold text-gray-900">{pendingPackage.credits.toLocaleString('tr-TR')}</span>
              </div>
              <div className="flex justify-between px-4 py-3 bg-blue-50/60">
                <span className="text-gray-500 font-medium">Ödenecek Tutar</span>
                <span className="font-bold text-blue-700 text-lg">₺{pendingPackage.price}</span>
              </div>
            </div>
            <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3 mb-4">
              <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-amber-200 text-amber-700">!</span>
              <p className="text-xs text-amber-800 leading-relaxed">
                Satın aldığınız krediler <strong>7 gün</strong> boyunca geçerlidir. Bu süre sonunda kullanılmayan krediler otomatik olarak silinir.
              </p>
            </div>
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => { setShowConfirm(false); setPendingPackage(null); }}
              >
                İptal
              </Button>
              <Button
                onClick={() => {
                  setShowConfirm(false);
                  handlePackageSelect(pendingPackage);
                }}
                disabled={loading}
              >
                {loading ? 'İşleniyor...' : 'Onayla ve Öde'}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Iyzico Checkout Form Container */}
      {selectedPackage && (
        <Card>
          <CardHeader>
            <CardTitle>Ödeme Bilgileri</CardTitle>
            <CardDescription>
              {selectedPackage.name} - ₺{selectedPackage.price}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div id="iyzico-checkout" className="w-full"></div>
          </CardContent>
        </Card>
      )}

      {/* FAQ Section */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Sıkça Sorulan Sorular</h2>
        <div className="space-y-4">
          {FAQS.map((faq, idx) => (
            <Card key={idx}>
              <CardHeader>
                <CardTitle className="text-lg">{faq.question}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">{faq.answer}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
