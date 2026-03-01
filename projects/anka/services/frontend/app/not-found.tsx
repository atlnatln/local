import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="text-center max-w-md space-y-6">
        <h1 className="text-7xl font-bold text-blue-600">404</h1>
        <h2 className="text-2xl font-semibold text-gray-900">
          Sayfa Bulunamadı
        </h2>
        <p className="text-gray-600">
          Aradığınız sayfa mevcut değil veya taşınmış olabilir.
        </p>
        <div className="flex gap-3 justify-center">
          <Link href="/dashboard">
            <Button>Kontrol Paneline Dön</Button>
          </Link>
          <Link href="/">
            <Button variant="outline">Ana Sayfa</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
