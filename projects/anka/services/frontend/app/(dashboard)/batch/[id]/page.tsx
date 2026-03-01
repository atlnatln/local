'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { fetchAPI } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/components/ToastProvider'
import { 
  CheckCircle2, 
  AlertCircle, 
  FileDown, 
  Search, 
  Filter, 
  Phone,
  Mail,
  ArrowLeft,
  Loader2,
  Plus,
  ExternalLink
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
  emails_enriched: number
  skipped_404: number
  aborted_reason?: string
  
  // Files
  csv_url?: string
  xlsx_url?: string

    // Items
    items: BatchItem[]
}

interface BatchItem {
    id: string
    firm_id: string
    firm_name: string
    is_verified: boolean
    has_error: boolean
    data: {
        phone?: string
        phone_number?: string
        nationalPhoneNumber?: string
        website?: string
        website_uri?: string
        websiteUri?: string
        email?: string
        address?: string
        formatted_address?: string
        formattedAddress?: string
    }
}

export default function BatchDetailPage() {
  const params = useParams()
  const [batch, setBatch] = useState<BatchDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [exportLoading, setExportLoading] = useState(false)
  const [exportCreated, setExportCreated] = useState(false)
  const { addToast } = useToast()

    const downloadItemsCsv = () => {
        if (!batch || !batch.items || batch.items.length === 0) return

        const headers = ['Firma', 'Telefon', 'Website', 'Email', 'Adres', 'Doğrulandı']
        const rows = batch.items.map((item) => {
            const phone = item.data?.phone || item.data?.phone_number || item.data?.nationalPhoneNumber || ''
            const website = item.data?.website || item.data?.website_uri || item.data?.websiteUri || ''
            const email = item.data?.email || ''
            const address = item.data?.address || item.data?.formatted_address || item.data?.formattedAddress || ''
            return [
                item.firm_name,
                phone,
                website,
                email,
                address,
                item.is_verified ? 'Evet' : 'Hayır',
            ]
        })

        const escapeCell = (value: string) => {
            let s = String(value);
            // CSV formula injection guard: prepend tab to cells starting with =, +, -, @, \t, \r, \n
            if (/^[=+\-@\t\r\n]/.test(s)) {
                s = `'${s}`;
            }
            return `"${s.replace(/"/g, '""')}"`;
        }
        const csv = [headers, ...rows].map((row) => row.map(escapeCell).join(',')).join('\n')
        const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8;' })
        const url = URL.createObjectURL(blob)

        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${batch.city}_${batch.sector}_${batch.id}.csv`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
    }

  useEffect(() => {
    let cancelled = false
    let timeoutId: NodeJS.Timeout

    async function loadBatch() {
      try {
        const data = await fetchAPI<BatchDetail>(`/batches/${params.id}/`)
        if (cancelled) return
        setBatch(data)
        setLoading(false)
        
        // Polling if not finished
        if (['CREATED', 'COLLECTING_IDS', 'FILTERING', 'ENRICHING_CONTACTS', 'ENRICHING_EMAILS'].includes(data.status)) {
            timeoutId = setTimeout(loadBatch, 2000)
        }
      } catch (err: any) {
        if (cancelled) return
        console.error(err)
        setError('Batch detayları yüklenirken bir hata oluştu.')
        setLoading(false)
      }
    }

    loadBatch()

    return () => {
        cancelled = true
        clearTimeout(timeoutId)
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
                    <CardDescription>4 Aşamalı doğrulama sürecinin sonuçları</CardDescription>
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
                                    <span className="text-lg font-bold text-emerald-700">{batch.contacts_enriched}</span>
                                </div>
                            </div>
                        </div>

                        {/* Stage 4 — Email Enrichment */}
                        <div className="relative">
                            <span className="absolute -left-[29px] top-0 w-3 h-3 rounded-full bg-violet-500 ring-4 ring-white"></span>
                            <div className="flex items-start justify-between">
                                <div>
                                    <h4 className="flex items-center gap-2 text-sm font-semibold text-slate-900">
                                        <Mail className="w-4 h-4 text-violet-600" />
                                        Email Zenginleştirme
                                    </h4>
                                    <p className="text-sm text-slate-500 mt-1">Web scraping ve AI ile bulunan email adresleri</p>
                                </div>
                                <div className="text-right">
                                    <span className="text-2xl font-bold text-violet-700">{batch.emails_enriched ?? 0}</span>
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
                                                disabled={!batch.csv_url && batch.items.length === 0}
                                                className="w-full justify-start"
                                                variant="outline"
                                                onClick={() => {
                                                    if (batch.csv_url) {
                                                        window.open(batch.csv_url, '_blank', 'noopener,noreferrer')
                                                        return
                                                    }
                                                    downloadItemsCsv()
                                                }}
                                        >
                        <FileDown className="mr-2 h-4 w-4" />
                                                {batch.csv_url ? 'CSV İndir' : 'CSV İndir (Tarayıcı)'}
                    </Button>
                    <Button 
                        disabled={!batch.xlsx_url} 
                        className="w-full justify-start" 
                        variant="outline"
                        onClick={() => {
                            if (!batch.xlsx_url) return
                            const link = document.createElement('a')
                            link.href = batch.xlsx_url
                            link.setAttribute('download', `${batch.city}-${batch.sector}-${batch.id}.xlsx`)
                            document.body.appendChild(link)
                            link.click()
                            document.body.removeChild(link)
                        }}
                    >
                        <FileDown className="mr-2 h-4 w-4" />
                        Excel (XLSX) İndir
                    </Button>
                    
                    {!batch.csv_url && !exportCreated && (isReady || isPartial) && (
                        <div className="space-y-2">
                            <Button
                                className="w-full justify-start"
                                variant="default"
                                disabled={exportLoading}
                                onClick={async () => {
                                    setExportLoading(true)
                                    try {
                                        const results = await Promise.allSettled([
                                            fetchAPI('/exports/', {
                                                method: 'POST',
                                                body: JSON.stringify({ batch: batch.id, format: 'csv' })
                                            }),
                                            fetchAPI('/exports/', {
                                                method: 'POST',
                                                body: JSON.stringify({ batch: batch.id, format: 'xlsx' })
                                            })
                                        ])
                                        const failures = results.filter(r => r.status === 'rejected')
                                        if (failures.length === 0) {
                                            setExportCreated(true)
                                            addToast('Export oluşturuldu! İndirilmişler sayfasından takip edebilirsiniz.', 'success')
                                        } else if (failures.length < results.length) {
                                            setExportCreated(true)
                                            addToast('Bazı export formatları oluşturuldu ancak bir kısmı hata aldı. İndirilmişler sayfasını kontrol edin.', 'warning')
                                        } else {
                                            throw new Error('Tüm export istekleri başarısız oldu.')
                                        }
                                    } catch (err) {
                                        console.error('Export oluşturma hatası:', err)
                                        addToast('Export oluşturulurken bir hata oluştu.', 'error')
                                    } finally {
                                        setExportLoading(false)
                                    }
                                }}
                            >
                                <Plus className="mr-2 h-4 w-4" />
                                {exportLoading ? 'Oluşturuluyor...' : 'Export Oluştur (CSV + XLSX)'}
                            </Button>
                            <p className="text-xs text-slate-400 text-center pt-1">Dosyalar hazırlanıyor, İndirilmişler sayfasından takip edebilirsiniz.</p>
                        </div>
                    )}
                    {exportCreated && (
                        <Link href="/exports" className="block">
                            <Button variant="default" className="w-full justify-start">
                                <ExternalLink className="mr-2 h-4 w-4" />
                                İndirilmişlere Git
                            </Button>
                        </Link>
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

            <Card>
                <CardHeader>
                    <CardTitle>Sonuçlar</CardTitle>
                    <CardDescription>Doğrulanan ve zenginleştirilen kayıtlar</CardDescription>
                </CardHeader>
                <CardContent>
                    {batch.items.length === 0 ? (
                        <p className="text-sm text-slate-500">Henüz gösterilecek kayıt yok.</p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left text-slate-500">
                                        <th className="py-2 pr-3">Firma</th>
                                        <th className="py-2 pr-3">Telefon</th>
                                        <th className="py-2 pr-3">Website</th>
                                        <th className="py-2 pr-3">Email</th>
                                        <th className="py-2 pr-3">Adres</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {batch.items.map((item) => {
                                        const phone = item.data?.phone || item.data?.phone_number || item.data?.nationalPhoneNumber || '-'
                                        const website = item.data?.website || item.data?.website_uri || item.data?.websiteUri || ''
                                        const email = item.data?.email || ''
                                        const address = item.data?.address || item.data?.formatted_address || item.data?.formattedAddress || '-'

                                        return (
                                            <tr key={item.id} className="border-b align-top">
                                                <td className="py-2 pr-3 font-medium text-slate-900">{item.firm_name}</td>
                                                <td className="py-2 pr-3 text-slate-700">{phone}</td>
                                                <td className="py-2 pr-3 text-slate-700">
                                                    {website ? (
                                                        <a
                                                            href={website.match(/^https?:\/\//) ? website : `https://${website}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="text-indigo-600 hover:underline break-all"
                                                        >
                                                            {website}
                                                        </a>
                                                    ) : (
                                                        '-'
                                                    )}
                                                </td>
                                                <td className="py-2 pr-3 text-slate-700">
                                                    {email ? (
                                                        <a href={`mailto:${email}`} className="text-indigo-600 hover:underline break-all">
                                                            {email}
                                                        </a>
                                                    ) : (
                                                        '-'
                                                    )}
                                                </td>
                                                <td className="py-2 pr-3 text-slate-700">{address}</td>
                                            </tr>
                                        )
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </CardContent>
            </Card>
    </div>
  )
}
