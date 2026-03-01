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
  const isCreated = batch.status === 'CREATED'
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
            {isCreated && <Badge variant="secondary" className="px-3 py-1 text-slate-500">Kuyruğa Alındı</Badge>}
            {isProcessing && !isCreated && <Badge variant="secondary" className="px-3 py-1 animate-pulse">İşleniyor</Badge>}
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
                    {(() => {
                        type StageKey = 'CREATED' | 'COLLECTING_IDS' | 'FILTERING' | 'ENRICHING_CONTACTS' | 'ENRICHING_EMAILS' | 'READY' | 'PARTIAL' | 'FAILED'
                        const STATUS_STAGE: Record<StageKey, number> = {
                            CREATED: 0,
                            COLLECTING_IDS: 1,
                            FILTERING: 2,
                            ENRICHING_CONTACTS: 3,
                            ENRICHING_EMAILS: 4,
                            READY: 5,
                            PARTIAL: 5,
                            FAILED: 5,
                        }
                        const currentStage = STATUS_STAGE[(batch.status as StageKey)] ?? 0

                        const isDone = batch.status === 'READY' || batch.status === 'PARTIAL'
                        const isFailed = batch.status === 'FAILED'

                        const stages = [
                            {
                                index: 1,
                                label: 'Aday Havuzu',
                                desc: 'Geniş tarama ile bulunan toplam kayıt',
                                icon: Search,
                                iconColor: 'text-slate-400',
                                valueColor: 'text-slate-700',
                                dotDone: 'bg-slate-400',
                                dotActive: 'bg-slate-400',
                                dotPending: 'bg-slate-200',
                                value: batch.ids_collected,
                                activeLabel: 'ID\'ler toplanıyor…',
                            },
                            {
                                index: 2,
                                label: 'Doğrulanmış Firma',
                                desc: 'İnsan-okunur adres doğrulaması geçen',
                                icon: Filter,
                                iconColor: 'text-indigo-500',
                                valueColor: 'text-indigo-600',
                                dotDone: 'bg-indigo-400',
                                dotActive: 'bg-indigo-500',
                                dotPending: 'bg-indigo-100',
                                value: batch.ids_verified,
                                activeLabel: 'Adresler doğrulanıyor…',
                            },
                            {
                                index: 3,
                                label: 'Zenginleştirilmiş İletişim',
                                desc: 'Telefon ve web bilgisi eklenen net liste',
                                icon: Phone,
                                iconColor: 'text-emerald-600',
                                valueColor: 'text-emerald-700',
                                dotDone: 'bg-emerald-400',
                                dotActive: 'bg-emerald-500',
                                dotPending: 'bg-emerald-100',
                                value: batch.contacts_enriched,
                                activeLabel: 'İletişim bilgileri zenginleştiriliyor…',
                            },
                            {
                                index: 4,
                                label: 'Email Zenginleştirme',
                                desc: 'Web scraping ve AI ile bulunan email adresleri',
                                icon: Mail,
                                iconColor: 'text-violet-600',
                                valueColor: 'text-violet-700',
                                dotDone: 'bg-violet-400',
                                dotActive: 'bg-violet-500',
                                dotPending: 'bg-violet-100',
                                value: batch.emails_enriched ?? 0,
                                activeLabel: 'Email adresleri aranıyor…',
                            },
                        ]

                        return (
                            <div className="relative pl-6 border-l-2 border-slate-100 space-y-8">
                                {stages.map((stage) => {
                                    const stageStatus = currentStage > stage.index
                                        ? 'done'
                                        : currentStage === stage.index
                                            ? 'active'
                                            : 'pending'
                                    const Icon = stage.icon
                                    const isActive = stageStatus === 'active' && !isDone && !isFailed
                                    const isDoneStage = stageStatus === 'done' || isDone

                                    return (
                                        <div key={stage.index} className={`relative transition-opacity duration-300 ${stageStatus === 'pending' && !isDone ? 'opacity-40' : 'opacity-100'}`}>
                                            {/* Timeline dot */}
                                            {isActive ? (
                                                <span className={`absolute -left-[29px] top-0 w-3 h-3 rounded-full ${stage.dotActive} ring-4 ring-white animate-pulse`} />
                                            ) : isDoneStage ? (
                                                <span className={`absolute -left-[31px] top-[-1px] flex items-center justify-center w-4 h-4`}>
                                                    <CheckCircle2 className={`w-4 h-4 ${stage.dotDone.replace('bg-', 'text-')}`} />
                                                </span>
                                            ) : (
                                                <span className={`absolute -left-[29px] top-0 w-3 h-3 rounded-full ${stage.dotPending} ring-4 ring-white`} />
                                            )}

                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className={`flex items-center gap-2 text-sm font-semibold ${isDoneStage ? 'text-slate-900' : isActive ? 'text-slate-900' : 'text-slate-400'}`}>
                                                        <Icon className={`w-4 h-4 ${isActive ? stage.iconColor : isDoneStage ? stage.iconColor : 'text-slate-300'}`} aria-hidden="true" />
                                                        {stage.label}
                                                        {isActive && (
                                                            <span className="inline-flex items-center gap-1 text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                                                                <Loader2 className="w-3 h-3 animate-spin" />
                                                                {stage.activeLabel}
                                                            </span>
                                                        )}
                                                    </h4>
                                                    <p className="text-sm text-slate-500 mt-1">{stage.desc}</p>
                                                    {stage.index === 2 && batch.skipped_404 > 0 && (
                                                        <span className="text-xs text-red-500 mt-1 block">
                                                            {batch.skipped_404} kayıt elendi (Bulunamadı/Doğrulanamadı)
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="text-right ml-4">
                                                    <span className={`font-bold ${isActive ? 'text-base ' + stage.valueColor : isDoneStage ? 'text-lg ' + stage.valueColor : 'text-base text-slate-300'}`}>
                                                        {isActive && stage.value === 0 ? (
                                                            <span className="inline-flex items-center gap-1">
                                                                <Loader2 className="w-3 h-3 animate-spin" />
                                                            </span>
                                                        ) : stage.value}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        )
                    })()}
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
