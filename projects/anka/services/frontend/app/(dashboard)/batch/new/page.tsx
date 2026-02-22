'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { fetchAPI } from '@/lib/api-client'
import { getCurrentUser } from '@/lib/auth'
import { formatError } from '@/lib/utils'

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
        if (!formData.city || !formData.sector || !formData.organization) {
            throw new Error('Lütfen şehir, sektör ve organizasyon seçiniz.')
        }

        const payload = {
          organization: formData.organization,
          city: formData.city,
          sector: formData.sector,
          filters: formData.district.trim() ? { district: formData.district.trim() } : {},
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

  if (loadingConfig) {
    return (
        <div className="flex items-center justify-center h-full p-8">
            <p>Yükleniyor...</p>
        </div>
    )
  }

  if (organizations.length === 0) {
      return (
          <div className="p-8">
              <Alert variant="destructive">
                  <AlertDescription>
                      Herhangi bir organizasyona üye değilsiniz. Lütfen önce bir organizasyon oluşturun veya davet isteyin.
                  </AlertDescription>
              </Alert>
          </div>
      )
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Yeni Sorgu (Batch) Oluştur</CardTitle>
          <CardDescription>
            Şehir ve sektör seçin. Sistem 3 aşamalı doğrulama ile iletişim ve website alanlarını üretir.
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

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                <Label htmlFor="city">Şehir</Label>
              <Input
                    id="city"
                    name="city"
                    value={formData.city}
                    onChange={handleChange}
                list="city-options"
                placeholder="Örn: Ankara"
                    required
              />
              <datalist id="city-options">
                {cities.map((city) => (
                <option key={city.id} value={city.name} />
                ))}
              </datalist>
              <p className="text-xs text-muted-foreground">Öneriden seçebilir veya doğal dilde yazabilirsiniz.</p>
                </div>

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
              <div className="flex gap-2">
                <Button type="button" variant="outline" onClick={() => setFormData(prev => ({ ...prev, record_count_estimate: 2 }))}>
                  2 Kayıt Deneme
                </Button>
                <Button type="button" variant="outline" onClick={() => setFormData(prev => ({ ...prev, record_count_estimate: 10 }))}>
                  10 Kayıt
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                  Bu değer kredi bloke ve pipeline planlaması için kullanılır. Üst sınır: {MAX_RECORD_ESTIMATE}.
              </p>
            </div>

            <div className="flex justify-end gap-4 pt-4">
              <Link href="/dashboard">
                <Button variant="outline" type="button">İptal</Button>
              </Link>
              <Button type="submit" disabled={loading}>
                {loading ? 'Oluşturuluyor...' : 'Batch Oluştur'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
