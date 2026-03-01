'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { fetchAPI } from '@/lib/api-client'
import { getCurrentUser } from '@/lib/auth'
import { formatError } from '@/lib/utils'
import type { LocationBounds } from '@/components/MapAreaSelector'

// Lazy-load map to avoid SSR issues with google.maps
const MapAreaSelector = dynamic(() => import('@/components/MapAreaSelector'), { ssr: false })

interface CatalogItem {
  id: string;
  name: string;
  code?: string;
}

interface CreatedBatch {
  id: string;
}

const MAX_RECORD_ESTIMATE = 50
const MIN_RECORD_ESTIMATE = 1

export default function NewBatchPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [loadingConfig, setLoadingConfig] = useState(true)
  const [error, setError] = useState('')
  
  const [cities, setCities] = useState<CatalogItem[]>([])
  const [sectors, setSectors] = useState<CatalogItem[]>([])
  const [organizations, setOrganizations] = useState<any[]>([])

  // Map mode toggle
  const [useMapArea, setUseMapArea] = useState(false)
  const [locationBounds, setLocationBounds] = useState<LocationBounds | null>(null)
  
  // Confirmation modal
  const [showConfirm, setShowConfirm] = useState(false)

  const [formData, setFormData] = useState({
    organization: '',
    city: '',
    sector: '',
    district: '',
    record_count_estimate: 2,
  })

  useEffect(() => {
    async function init() {
      try {
        const [citiesData, sectorsData, userData] = await Promise.all([
           fetchAPI<{results: CatalogItem[]}>('/catalog/cities/'),
           fetchAPI<{results: CatalogItem[]}>('/catalog/sectors/'),
           getCurrentUser()
        ])
        
        setCities(citiesData.results || [])
        setSectors(sectorsData.results || [])
        
        const userOrgs = userData.organizations || []
        setOrganizations(userOrgs)
        
        if (userOrgs.length > 0) {
            setFormData(prev => ({ ...prev, organization: userOrgs[0].id }))
        }
      } catch (err) {
        console.error(err)
        setError('Konfigürasyon yüklenemedi. Lütfen sayfayı yenileyin.')
      } finally {
        setLoadingConfig(false)
      }
    }
    init()
  }, [])

  const handleBoundsChange = useCallback((bounds: LocationBounds | null) => {
    setLocationBounds(bounds)
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target

    if (name === 'record_count_estimate') {
      const numericValue = Number(value)
      const safeValue = Number.isFinite(numericValue)
        ? Math.min(MAX_RECORD_ESTIMATE, Math.max(MIN_RECORD_ESTIMATE, numericValue))
        : MIN_RECORD_ESTIMATE

      setFormData(prev => ({
        ...prev,
        record_count_estimate: safeValue,
      }))
      return
    }

    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
  }

  // --- Validate & open confirmation modal ---
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!formData.sector || !formData.organization) {
      setError('Lütfen sektör ve organizasyon seçiniz.')
      return
    }
    if (!useMapArea && !formData.city) {
      setError('Lütfen şehir seçiniz veya harita ile alan belirleyiniz.')
      return
    }
    if (useMapArea && !locationBounds) {
      setError('Lütfen harita üzerinde dörtgen çizerek arama alanını belirleyiniz.')
      return
    }

    setShowConfirm(true)
  }

  // --- Confirmed → send to API ---
  const handleConfirmedSubmit = async () => {
    setShowConfirm(false)
    setLoading(true)
    setError('')
    
    try {
        const filters: Record<string, any> = {}
        if (formData.district.trim()) {
          filters.district = formData.district.trim()
        }
        if (useMapArea && locationBounds) {
          filters.location_bounds = locationBounds
        }

        const payload = {
          organization: formData.organization,
          city: useMapArea ? (formData.city || 'Harita Alanı') : formData.city,
          sector: formData.sector,
          filters,
          record_count_estimate: Math.min(MAX_RECORD_ESTIMATE, Math.max(MIN_RECORD_ESTIMATE, Number(formData.record_count_estimate)))
        }

        const createdBatch = await fetchAPI<CreatedBatch>('/batches/', {
            method: 'POST',
          body: JSON.stringify(payload)
        })
        router.push(`/batch/${createdBatch.id}`)
    } catch (err) {
        setError(formatError(err))
    } finally {
        setLoading(false)
    }
  }

  // --- Helpers for display labels ---
  const getOrgName = () => {
    const org = organizations.find((o) => String(o.id) === String(formData.organization))
    return org?.name || formData.organization
  }

  const getLocationLabel = () => {
    if (useMapArea) {
      const label = formData.city || 'Harita Alanı'
      if (locationBounds) {
        const sw = locationBounds.low
        const ne = locationBounds.high
        return `${label} (${sw.latitude.toFixed(4)}, ${sw.longitude.toFixed(4)} → ${ne.latitude.toFixed(4)}, ${ne.longitude.toFixed(4)})`
      }
      return label
    }
    const parts = [formData.city]
    if (formData.district.trim()) parts.push(formData.district.trim())
    return parts.join(' / ')
  }

  if (loadingConfig) {
    return (
        <div className="flex items-center justify-center h-full p-8">
            <p>Yükleniyor...</p>
        </div>
    )
  }

  if (organizations.length === 0) {
      return (
          <div className="p-8 max-w-lg mx-auto space-y-4">
              <Alert variant="destructive">
                  <AlertDescription>
                      Herhangi bir organizasyona üye değilsiniz. Lütfen önce bir organizasyon oluşturun veya davet isteyin.
                  </AlertDescription>
              </Alert>
              <p className="text-sm text-gray-600">
                Organizasyon otomatik olarak hesap oluşturulduğunda eklenir. Sorun devam ediyorsa destek ile iletişime geçin.
              </p>
              <div className="flex gap-3">
                <Link href="/dashboard">
                  <Button variant="outline">Dashboard'a Dön</Button>
                </Link>
              </div>
          </div>
      )
  }

  return (
    <div className="max-w-3xl mx-auto py-4 sm:py-8">
      <Card>
        <CardHeader>
          <CardTitle>Yeni Sorgu (Batch) Oluştur</CardTitle>
          <CardDescription>
            Şehir ve sektör seçin veya harita üzerinden alan çizerek arama yapın. Sistem 3 aşamalı doğrulama ile iletişim ve website alanlarını üretir.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <Alert>
              <AlertDescription>
                Düşük maliyetli başlangıç için önce <strong>2 kayıt</strong> ile deneme önerilir.
              </AlertDescription>
            </Alert>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="organization">Organizasyon</Label>
              <select
                id="organization"
                name="organization"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                value={formData.organization}
                onChange={handleChange}
                required
              >
                {organizations.map((org) => (
                  <option key={org.id} value={org.id}>
                    {org.name}
                  </option>
                ))}
              </select>
            </div>

            {/* --- Konum Seçim Modu --- */}
            <div className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
                <Label className="text-base font-semibold">Konum Seçimi</Label>
                <div className="flex rounded-md border border-input overflow-hidden text-sm">
                  <button
                    type="button"
                    className={`px-3 py-1.5 transition-colors ${!useMapArea ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'}`}
                    onClick={() => setUseMapArea(false)}
                  >
                    Şehir / İlçe
                  </button>
                  <button
                    type="button"
                    className={`px-3 py-1.5 transition-colors ${useMapArea ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-muted'}`}
                    onClick={() => setUseMapArea(true)}
                  >
                    Harita ile Seç
                  </button>
                </div>
              </div>

              {!useMapArea ? (
                /* Classic city/district mode */
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="city">Şehir</Label>
                      <Input
                        id="city"
                        name="city"
                        value={formData.city}
                        onChange={handleChange}
                        list="city-options"
                        placeholder="Örn: Ankara"
                        required={!useMapArea}
                      />
                      <datalist id="city-options">
                        {cities.map((city) => (
                          <option key={city.id} value={city.name} />
                        ))}
                      </datalist>
                      <p className="text-xs text-muted-foreground">Öneriden seçebilir veya doğal dilde yazabilirsiniz.</p>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="district">İlçe (Opsiyonel)</Label>
                      <Input
                        id="district"
                        name="district"
                        value={formData.district}
                        onChange={handleChange}
                        placeholder="Örn: Menteşe"
                      />
                      <p className="text-xs text-muted-foreground">
                        Arama sonuçlarını belirli bir ilçeyle sınırlandırır.
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                /* Map rectangle mode */
                <div className="space-y-3">
                  <MapAreaSelector
                    onBoundsChange={handleBoundsChange}
                    initialBounds={locationBounds}
                    height="min(380px, 50vh)"
                  />
                  <div className="space-y-2">
                    <Label htmlFor="city">Şehir Etiketi (Opsiyonel)</Label>
                    <Input
                      id="city"
                      name="city"
                      value={formData.city}
                      onChange={handleChange}
                      placeholder="Örn: İstanbul Anadolu Yakası"
                    />
                    <p className="text-xs text-muted-foreground">
                      Harita alanı seçtiyseniz şehir adını etiket olarak girebilirsiniz. Boş bırakırsanız &quot;Harita Alanı&quot; olarak kaydedilir.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Sektör */}
            <div className="space-y-2">
              <Label htmlFor="sector">Sektör</Label>
              <Input
                id="sector"
                name="sector"
                value={formData.sector}
                onChange={handleChange}
                list="sector-options"
                placeholder="Örn: şehir plancısı"
                required
              />
              <datalist id="sector-options">
                {sectors.map((sector) => (
                  <option key={sector.id} value={sector.name} />
                ))}
              </datalist>
              <p className="text-xs text-muted-foreground">Kategoriyi sade tutun; konumu şehir alanında verin.</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="record_count_estimate">Tahmini Kayıt Sayısı</Label>
              <Input
                id="record_count_estimate"
                name="record_count_estimate"
                type="number"
                min={String(MIN_RECORD_ESTIMATE)}
                max={String(MAX_RECORD_ESTIMATE)}
                value={formData.record_count_estimate}
                onChange={handleChange}
                required
              />
              <div className="flex flex-wrap gap-2">
                <Button type="button" variant="outline" size="sm" onClick={() => setFormData(prev => ({ ...prev, record_count_estimate: 2 }))}>
                  2 Kayıt Deneme
                </Button>
                <Button type="button" variant="outline" size="sm" onClick={() => setFormData(prev => ({ ...prev, record_count_estimate: 10 }))}>
                  10 Kayıt
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                  Bu değer kredi bloke ve pipeline planlaması için kullanılır. Üst sınır: {MAX_RECORD_ESTIMATE}.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4">
              <Link href="/dashboard" className="w-full sm:w-auto">
                <Button variant="outline" type="button" className="w-full sm:w-auto">İptal</Button>
              </Link>
              <Button type="submit" disabled={loading} className="w-full sm:w-auto">
                {loading ? 'Oluşturuluyor...' : 'Batch Oluştur'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* ─── Onay Modalı (Banka Havalesi Stili) ─── */}
      <Dialog open={showConfirm} onOpenChange={setShowConfirm}>
        <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto mx-4 sm:mx-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-lg">
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
              </span>
              Sorgu Onayı
            </DialogTitle>
            <DialogDescription>
              Aşağıdaki bilgileri kontrol edin ve onaylayın.
            </DialogDescription>
          </DialogHeader>

          <div className="rounded-lg border border-gray-200 bg-gray-50/60 divide-y divide-gray-200 text-sm">
            {/* Organizasyon */}
            <div className="flex justify-between px-4 py-3">
              <span className="text-gray-500 font-medium">Organizasyon</span>
              <span className="text-gray-900 font-semibold text-right max-w-[60%] truncate">
                {getOrgName()}
              </span>
            </div>

            {/* Konum */}
            <div className="flex flex-col sm:flex-row sm:justify-between px-4 py-3 gap-1">
              <span className="text-gray-500 font-medium">Konum</span>
              <span className="text-gray-900 font-semibold sm:text-right sm:max-w-[60%] break-words text-sm">
                {getLocationLabel()}
              </span>
            </div>

            {/* Konum Tipi */}
            <div className="flex justify-between px-4 py-3">
              <span className="text-gray-500 font-medium">Konum Tipi</span>
              <span className="text-gray-900">
                {useMapArea ? (
                  <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-700">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
                    Harita Alanı
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-700">
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/></svg>
                    Şehir / İlçe
                  </span>
                )}
              </span>
            </div>

            {/* Sektör */}
            <div className="flex justify-between px-4 py-3">
              <span className="text-gray-500 font-medium">Sektör</span>
              <span className="text-gray-900 font-semibold text-right max-w-[60%] truncate">
                {formData.sector}
              </span>
            </div>

            {/* Kayıt Sayısı */}
            <div className="flex justify-between px-4 py-3 bg-blue-50/60">
              <span className="text-gray-500 font-medium">Kayıt Sayısı</span>
              <span className="text-blue-700 font-bold text-lg">
                {formData.record_count_estimate}
              </span>
            </div>
          </div>

          {/* Kredi Uyarısı */}
          <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-3">
            <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-amber-200 text-amber-700">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            </span>
            <p className="text-xs text-amber-800 leading-relaxed">
              Bu işlem başlatıldığında <strong>{formData.record_count_estimate} kredi</strong> bloke edilecektir.
              İşlem tamamlandıktan sonra kullanılmayan krediler iade edilir.
            </p>
          </div>

          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="outline"
              onClick={() => setShowConfirm(false)}
              className="flex-1 sm:flex-none"
            >
              Düzenle
            </Button>
            <Button
              onClick={handleConfirmedSubmit}
              disabled={loading}
              className="flex-1 sm:flex-none"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                  Oluşturuluyor…
                </span>
              ) : (
                'Onayla ve Başlat'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
