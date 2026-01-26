'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Welcome section */}
      <section>
        <h1 className="text-3xl font-bold text-gray-900">Hoş geldiniz!</h1>
        <p className="mt-2 text-gray-600">
          Anka'yı kullanarak verilerinizi yönetebilir, toplu işlemler yapabilir ve ödemeyi yönetebilirsiniz.
        </p>
      </section>

      {/* Quick actions */}
      <section className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-blue-600">
          <CardHeader>
            <CardTitle className="text-lg">Yeni Batch</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-gray-600">
              Yeni bir toplu veri işlem işlemi başlatın
            </p>
            <Link href="/batch/new">
              <Button className="w-full">Başla</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-600">
          <CardHeader>
            <CardTitle className="text-lg">Krediler</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-gray-600">
              Kredi paketleri satın alın
            </p>
            <Link href="/checkout">
              <Button className="w-full">Satın Al</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-600">
          <CardHeader>
            <CardTitle className="text-lg">İndirilmişler</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-gray-600">
              Dışa aktarılmış dosyaları görüntüleyin
            </p>
            <Link href="/exports">
              <Button className="w-full">Görüntüle</Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-red-600">
          <CardHeader>
            <CardTitle className="text-lg">İtirazlar</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-gray-600">
              Dispütleri yönetin
            </p>
            <Link href="/disputes">
              <Button className="w-full">Yönet</Button>
            </Link>
          </CardContent>
        </Card>
      </section>

      {/* Stats section */}
      <section className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600">
              Aktif Batchler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-gray-900">0</p>
            <p className="mt-2 text-sm text-gray-500">
              Son 30 günde
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600">
              Kullanılan Krediler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-gray-900">0</p>
            <p className="mt-2 text-sm text-gray-500">
              Bu ay
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600">
              Açık İtirazlar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold text-gray-900">0</p>
            <p className="mt-2 text-sm text-gray-500">
              Bekleme durumunda
            </p>
          </CardContent>
        </Card>
      </section>

      {/* Recent activity */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle>Son Aktiviteler</CardTitle>
            <CardDescription>
              En son yapılan işlemleriniz
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center text-gray-500 py-8">
              <p>Henüz aktivite yok</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
