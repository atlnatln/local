'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { fetchAPI } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  CheckCircle2, 
  AlertCircle, 
  FileDown, 
  Search, 
  Filter, 
  Phone,
  ArrowLeft,
  Loader2
} from 'lucide-react'

interface BatchDetail {
  id: string
  city: string
  sector: string
  status: string
  created_at: string
  completed_at: string | null
  
  // Stats
  ids_collected: number
  ids_verified: number
  contacts_enriched: number
  skipped_404: number
  aborted_reason?: string
  
  // Files
  csv_url?: string
  xlsx_url?: string
}

export default function BatchDetailPage() {
  const params = useParams()
  const [batch, setBatch] = useState<BatchDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let intervalId: NodeJS.Timeout

    async function loadBatch() {
      try {
        const data = await fetchAPI<BatchDetail>(`/batches/${params.id}/`)
        setBatch(data)
        
        // Polling if not finished
        if (['CREATED', 'COLLECTING_IDS', 'FILTERING', 'ENRICHING_CONTACTS'].includes(data.status)) {
            intervalId = setTimeout(loadBatch, 2000)
        } else {
            setLoading(false)
        }
      } catch (err: any) {
        console.error(err)
        setError('Batch detayları yüklenirken bir hata oluştu.')
        setLoading(false)
      }
    }

    loadBatch()

    return () => {
        if (intervalId) clearTimeout(intervalId)
    }
  }, [params.id])

  if (loading && !batch) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600 mb-4" />
        <p className="text-slate-500">Veriler yükleniyor...</p>
      </div>
    )
  }

  if (error || !batch) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Hata</AlertTitle>
          <AlertDescription>{error || 'Batch bulunamadı.'}</AlertDescription>
        </Alert>
        <div className="mt-4">
            <Link href="/dashboard">
                <Button variant="outline"> <ArrowLeft className="w-4 h-4 mr-2" /> Geri Dön</Button>
            </Link>
        </div>
      </div>
    )
  }

  const isPartial = batch.status === 'PARTIAL'
  const isReady = batch.status === 'READY'
  const isFailed = batch.status === 'FAILED'
  const isProcessing = !isReady && !isPartial && !isFailed

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8">
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-slate-500 mb-1">
                <Link href="/dashboard" className="hover:text-slate-800 transition-colors">Dashboard</Link>
                <span>/</span>
                <span>Batch Detayı</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                {batch.city} - {batch.sector}
            </h1>
            <p className="text-slate-500 text-sm">
                ID: {batch.id} • {new Date(batch.created_at).toLocaleDateString('tr-TR')}
            </p>
        </div>

        <div className="flex items-center gap-2">
            {isProcessing && <Badge variant="secondary" className="px-3 py-1 animate-pulse">İşleniyor</Badge>}
            {isReady && <Badge className="bg-green-100 text-green-800 hover:bg-green-200 border-green-200 px-3 py-1">Hazır</Badge>}
            {isPartial && <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200 px-3 py-1">Kısmen Tamamlandı</Badge>}
            {isFailed && <Badge variant="destructive" className="px-3 py-1">Başarısız</Badge>}
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="grid lg:grid-cols-3 gap-6">
        
        {/* Left Column: Stats & Status */}
        <div className="lg:col-span-2 space-y-6">
            
            {/* Status Message Card */}
            {(isReady || isPartial) && (
                <Alert className={`${isPartial ? 'bg-amber-50 border-amber-200' : 'bg-green-50 border-green-200'}`}>
                    {isReady ? <CheckCircle2 className="h-5 w-5 text-green-600" /> : <AlertCircle className="h-5 w-5 text-amber-600" />}
                    <div className="ml-2">
                        <AlertTitle className={`${isPartial ? 'text-amber-800' : 'text-green-800'} font-semibold`}>
                            {isReady ? 'Liste Hazır' : 'Sorgu Kısmen Tamamlandı'}
                        </AlertTitle>
                        <AlertDescription className={`${isPartial ? 'text-amber-700' : 'text-green-700'} mt-1`}>
                            {isReady 
                                ? 'Veri seti başarıyla oluşturuldu ve doğrulamadan geçti.' 
                                : 'Sistem, kaliteyi korumak için işlemi erken durdurdu.'}
                            
                            {isPartial && batch.aborted_reason && (
                                <div className="mt-2 text-sm font-medium bg-amber-100/50 p-2 rounded">
                                    Sebep: {batch.aborted_reason}
                                </div>
                            )}
                            
                            <p className="mt-2 text-xs opacity-80 font-medium">
                                * Teslim edilen kayıtlar faturalandırılır.
                            </p>
                        </AlertDescription>
                    </div>
                </Alert>
            )}

            {/* Pipeline Summary Card */}
            <Card>
                <CardHeader>
                    <CardTitle>İşlem Özeti</CardTitle>
                    <CardDescription>3 Aşamalı doğrulama sürecinin sonuçları</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="relative pl-6 border-l-2 border-slate-100 space-y-8">
                        
                        {/* Stage 1 */}
                        <div className="relative">
                            <span className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-slate-200 ring-4 ring-white"></span>
                            <div className="flex items-start justify-between">
                                <div>
                                    <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                                        <Search className="w-4 h-4 text-slate-400" />
                                        Aday Havuzu
                                    </h4>
                                    <p className="text-sm text-slate-500 mt-1">Geniş tarama ile bulunan toplam kayıt</p>
                                </div>
                                <div className="text-right">
                                    <span className="text-lg font-bold text-slate-700">{batch.ids_collected}</span>
                                </div>
                            </div>
                        </div>

                        {/* Stage 2 */}
                        <div className="relative">
                            <span className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-indigo-200 ring-4 ring-white"></span>
                            <div className="flex items-start justify-between">
                                <div>
                                    <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                                        <Filter className="w-4 h-4 text-indigo-500" />
                                        Doğrulanmış Firma
                                    </h4>
                                    <p className="text-sm text-slate-500 mt-1">İnsan-okunur adres doğrulaması geçen</p>
                                    {batch.skipped_404 > 0 && (
                                        <span className="text-xs text-red-500 mt-1 block">
                                            {batch.skipped_404} kayıt elendi (Bulunamadı/Doğrulanamadı)
                                        </span>
                                    )}
                                </div>
                                <div className="text-right">
                                    <span className="text-lg font-bold text-indigo-600">{batch.ids_verified}</span>
                                </div>
                            </div>
                        </div>

                        {/* Stage 3 */}
                        <div className="relative">
                            <span className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-white"></span>
                            <div className="flex items-start justify-between">
                                <div>
                                    <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                                        <Phone className="w-4 h-4 text-emerald-600" />
                                        Zenginleştirilmiş İletişim
                                    </h4>
                                    <p className="text-sm text-slate-500 mt-1">Telefon ve web bilgisi eklenen net liste</p>
                                </div>
                                <div className="text-right">
                                    <span className="text-2xl font-bold text-emerald-700">{batch.contacts_enriched}</span>
                                </div>
                            </div>
                        </div>

                    </div>
                </CardContent>
            </Card>

        </div>

        {/* Right Column: Downloads & Actions */}
        <div className="space-y-6">
            <Card className="bg-slate-50 border-slate-200">
                <CardHeader>
                    <CardTitle className="text-base">Dosyalar</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                    <Button 
                        disabled={!batch.csv_url} 
                        className="w-full justify-start" 
                        variant="outline"
                        onClick={() => batch.csv_url && window.open(batch.csv_url, '_blank')}
                    >
                        <FileDown className="mr-2 h-4 w-4" />
                        CSV İndir
                    </Button>
                    <Button 
                        disabled={!batch.xlsx_url} 
                        className="w-full justify-start" 
                        variant="outline"
                    >
                        <FileDown className="mr-2 h-4 w-4" />
                        Excel (XLSX) İndir
                    </Button>
                    
                    {!batch.csv_url && (isReady || isPartial) && (
                         <p className="text-xs text-slate-400 text-center pt-2">Dosyalar hazırlanıyor...</p>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Maliyet Detayı</CardTitle>
                </CardHeader>
                <CardContent className="text-sm space-y-4">
                     <div className="flex justify-between pb-2 border-b">
                        <span className="text-slate-500">Birim Maliyet</span>
                        <span className="font-medium">1 Kredi / Kayıt</span>
                     </div>
                     <div className="flex justify-between items-center">
                        <span className="text-slate-900 font-bold">Toplam Kesinti</span>
                        <span className="font-bold text-indigo-600 text-lg">{batch.contacts_enriched} Kredi</span>
                     </div>
                     <p className="text-xs text-slate-400">
                        * Sadece final teslim edilen (Zenginleştirilmiş) kayıt adedi kadar düşülmüştür.
                     </p>
                </CardContent>
            </Card>
        </div>

      </div>
    </div>
  )
}
