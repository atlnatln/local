'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function ExportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">İndirilmişler</h1>
        <p className="mt-2 text-gray-600">
          Tamamlanmış batch işlemlerini ve dışa aktarılmış dosyaları görüntüleyin
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dışa Aktarılmış Dosyalar</CardTitle>
          <CardDescription>
            İşlenen batch'lerden oluşturulan dosyalar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Dışa aktarılmış dosya yok</h3>
            <p className="text-sm text-gray-600 mb-4">
              Batch işlemlerini tamamladığınızda burada indirmek için hazır olacaklar
            </p>
            <Button>
              Yeni Batch Oluştur
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Yardım</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>
            • Dışa aktarılan dosyalar 7 gün boyunca mevcuttur
          </p>
          <p>
            • CSV ve Excel formatlarında indirebilirsiniz
          </p>
          <p>
            • Büyük dosyalar ZIP olarak paketlenebilir
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
