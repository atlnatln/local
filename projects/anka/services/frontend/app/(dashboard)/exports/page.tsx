'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { fetchAPI } from '@/lib/api-client'

interface Export {
  id: string
  batch: string
  format: 'csv' | 'xlsx'
  status: string
  signed_url: string
  signed_url_expires_at: string
  total_rows: number
  file_size: number
  error_message: string
  created_at: string
  completed_at: string
}

interface Batch {
  id: string
  city: string
  sector: string
  status: string
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('tr-TR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function isExpired(iso: string): boolean {
  return new Date(iso) < new Date()
}

export default function ExportsPage() {
  const [exports, setExports] = useState<Export[]>([])
  const [batches, setBatches] = useState<Record<string, Batch>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const [exportsData, batchesData] = await Promise.all([
          fetchAPI<{ results: Export[] }>('/exports/'),
          fetchAPI<{ results: Batch[] }>('/batches/'),
        ])
        setExports(exportsData.results)
        const batchMap: Record<string, Batch> = {}
        batchesData.results.forEach((b) => { batchMap[b.id] = b })
        setBatches(batchMap)
      } catch {
        setError('Dışa aktarımlar yüklenirken hata oluştu.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  function handleDownload(exp: Export) {
    if (!exp.signed_url) return
    const ext = exp.format
    const batch = batches[exp.batch]
    const name = batch
      ? `${batch.city}-${batch.sector}-${exp.batch}.${ext}`
      : `export-${exp.id}.${ext}`
    const link = document.createElement('a')
    link.href = exp.signed_url
    link.setAttribute('download', name)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const completedExports = exports.filter((e) => e.status === 'completed')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">İndirilmişler</h1>
          <p className="mt-2 text-gray-600">
            Tamamlanmış batch işlemlerinden oluşturulan dosyalar
          </p>
        </div>
        <Link href="/batch/new">
          <Button>Yeni Batch Oluştur</Button>
        </Link>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Dışa Aktarılmış Dosyalar</CardTitle>
          <CardDescription>
            {completedExports.length > 0
              ? `${completedExports.length} dosya mevcut`
              : 'Henüz dosya yok'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading && (
            <p className="text-center py-8 text-gray-500">Yükleniyor...</p>
          )}
          {error && (
            <p className="text-center py-8 text-red-500">{error}</p>
          )}
          {!loading && !error && completedExports.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Dışa aktarılmış dosya yok</h3>
              <p className="text-sm text-gray-600 mb-4">
                Batch işlemlerini tamamladığınızda burada indirmek için hazır olacaklar
              </p>
              <Link href="/batch/new">
                <Button>Yeni Batch Oluştur</Button>
              </Link>
            </div>
          )}
          {!loading && !error && completedExports.length > 0 && (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-gray-500">
                    <th className="pb-3 pr-4 font-medium">Batch</th>
                    <th className="pb-3 pr-4 font-medium">Format</th>
                    <th className="pb-3 pr-4 font-medium">Kayıt</th>
                    <th className="pb-3 pr-4 font-medium">Boyut</th>
                    <th className="pb-3 pr-4 font-medium">Tarih</th>
                    <th className="pb-3 font-medium">İndir</th>
                  </tr>
                </thead>
                <tbody>
                  {completedExports.map((exp) => {
                    const batch = batches[exp.batch]
                    const expired = isExpired(exp.signed_url_expires_at)
                    return (
                      <tr key={exp.id} className="border-b last:border-0 hover:bg-gray-50">
                        <td className="py-3 pr-4">
                          {batch ? (
                            <Link
                              href={`/batch/${exp.batch}`}
                              className="font-medium text-blue-600 hover:underline"
                            >
                              {batch.city} – {batch.sector}
                            </Link>
                          ) : (
                            <span className="text-gray-400 font-mono text-xs">{exp.batch.slice(0, 8)}…</span>
                          )}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold ${
                            exp.format === 'xlsx'
                              ? 'bg-green-100 text-green-700'
                              : 'bg-blue-100 text-blue-700'
                          }`}>
                            {exp.format.toUpperCase()}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-gray-700">{exp.total_rows}</td>
                        <td className="py-3 pr-4 text-gray-500">{formatBytes(exp.file_size)}</td>
                        <td className="py-3 pr-4 text-gray-500 whitespace-nowrap">{formatDate(exp.created_at)}</td>
                        <td className="py-3">
                          {expired ? (
                            <span className="text-xs text-red-400">Süresi doldu</span>
                          ) : (
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleDownload(exp)}
                            >
                              ↓ İndir
                            </Button>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Bilgi</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-600 space-y-2">
          <p>• Dışa aktarılan dosyalar 24 saat boyunca indirilebilir</p>
          <p>• CSV ve Excel (XLSX) formatlarında indirebilirsiniz</p>
          <p>• Süresi dolan dosyalar için batch detayından yeniden oluşturabilirsiniz</p>
        </CardContent>
      </Card>
    </div>
  )
}
