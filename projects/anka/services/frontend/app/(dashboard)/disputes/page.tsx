'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function DisputesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">İtirazlar</h1>
          <p className="mt-2 text-gray-600">
            Veri doğruluğu ile ilgili itirazları yönetin
          </p>
        </div>
        <Link href="/disputes/new">
          <Button>
            Yeni İtiraza
          </Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Açık İtirazlar</CardTitle>
          <CardDescription>
            Bekleme durumunda olan itirazlarınız
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Açık itiraza yok</h3>
            <p className="text-sm text-gray-600">
              Tüm itirazlarınız çözülmüştür
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tamamlanmış İtirazlar</CardTitle>
          <CardDescription>
            Çözümlenmiş itirazlarınız
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Tamamlanmış itiraza yok</h3>
            <p className="text-sm text-gray-600">
              Henüz itiraz dosyası bulunmamaktadır
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Otomatik Çözüm Kuralları</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>
            • İtirazlar yapılandırılmış kurallara göre otomatik olarak çözülür
          </p>
          <p>
            • Reddedilen itirazlar manuel inceleme için işaretlenebilir
          </p>
          <p>
            • Onarılan veriler otomatik olarak sistem tarafından güncellenir
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
