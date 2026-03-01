'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { getCurrentUser, changePassword, User } from '@/lib/auth'
import { fetchAPI } from '@/lib/api-client'

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [balance, setBalance] = useState<number | null>(null)
  const [orgName, setOrgName] = useState<string | null>(null)

  // Password form
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [pwLoading, setPwLoading] = useState(false)
  const [pwSuccess, setPwSuccess] = useState('')
  const [pwError, setPwError] = useState('')

  useEffect(() => {
    async function load() {
      try {
        const u = await getCurrentUser()
        setUser(u)
      } catch { /* auth guard in layout handles this */ }

      try {
        // Backend returns CreditPackage[] array (from ledger CreditBalanceView)
        const creditRaw = await fetchAPI<Array<{ balance: string }> | { balance: string }>('/credits/balance/')
        const creditArr = Array.isArray(creditRaw) ? creditRaw : (creditRaw ? [creditRaw] : [])
        const total = creditArr.reduce((sum, pkg) => {
          const val = parseFloat(pkg.balance || '0')
          return sum + (isNaN(val) ? 0 : val)
        }, 0)
        setBalance(total)
      } catch { /* non-critical */ }

      try {
        // Organizations are under /auth/ prefix (accounts app)
        const data = await fetchAPI<{ results: { name: string }[] }>('/auth/organizations/')
        if (data.results?.length > 0) {
          setOrgName(data.results[0].name)
        }
      } catch { /* non-critical */ }
    }
    load()
  }, [])

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault()
    setPwError('')
    setPwSuccess('')

    if (newPassword !== newPassword2) {
      setPwError('Yeni şifreler eşleşmiyor.')
      return
    }
    if (newPassword.length < 8) {
      setPwError('Yeni şifre en az 8 karakter olmalıdır.')
      return
    }

    setPwLoading(true)
    try {
      await changePassword(oldPassword, newPassword, newPassword2)
      setPwSuccess('Şifreniz başarıyla değiştirildi.')
      setOldPassword('')
      setNewPassword('')
      setNewPassword2('')
    } catch (err: any) {
      // fetchAPI throws an Error with detail/error message baked in
      const msg = err?.message || 'Şifre değiştirilirken bir hata oluştu.'
      setPwError(typeof msg === 'string' ? msg : JSON.stringify(msg))
    } finally {
      setPwLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Ayarlar</h1>
        <p className="mt-2 text-gray-600">Hesap bilgileri ve tercihleriniz</p>
      </div>

      {/* Account Info */}
      <Card>
        <CardHeader>
          <CardTitle>Hesap Bilgileri</CardTitle>
          <CardDescription>Google ile bağlı hesabınız</CardDescription>
        </CardHeader>
        <CardContent>
          {user ? (
            <dl className="space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Kullanıcı Adı</dt>
                <dd className="font-medium text-gray-900">{user.username}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">E-posta</dt>
                <dd className="font-medium text-gray-900">{user.email}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Ad Soyad</dt>
                <dd className="font-medium text-gray-900">
                  {user.first_name || user.last_name
                    ? `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim()
                    : '—'}
                </dd>
              </div>
              {orgName && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Organizasyon</dt>
                  <dd className="font-medium text-gray-900">{orgName}</dd>
                </div>
              )}
              {balance !== null && (
                <div className="flex justify-between">
                  <dt className="text-gray-500">Kredi Bakiyesi</dt>
                  <dd className="font-bold text-blue-600">{Math.round(balance).toLocaleString('tr-TR')}</dd>
                </div>
              )}
            </dl>
          ) : (
            <p className="text-gray-400 text-sm">Yükleniyor...</p>
          )}
        </CardContent>
      </Card>

      {/* Change Password */}
      <Card>
        <CardHeader>
          <CardTitle>Şifre Değiştir</CardTitle>
          <CardDescription>
            {!user?.has_usable_password
              ? 'Google ile giriş yaptığınız için şifre değiştirme kullanılamaz.'
              : 'Hesap şifrenizi güncelleyin'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!user?.has_usable_password ? (
            <div className="rounded-md bg-blue-50 border border-blue-200 p-4 text-sm text-blue-700">
              Google hesabınızla giriş yaptığınız için şifre belirlemenize gerek yoktur.
              Hesap güvenliğiniz Google&apos;ın iki faktörlü doğrulaması ile sağlanmaktadır.
            </div>
          ) : (
            <>
          {pwSuccess && (
            <Alert className="mb-4 border-green-200 bg-green-50">
              <AlertTitle className="text-green-700">Başarılı</AlertTitle>
              <AlertDescription className="text-green-600">{pwSuccess}</AlertDescription>
            </Alert>
          )}
          {pwError && (
            <Alert variant="destructive" className="mb-4">
              <AlertTitle>Hata</AlertTitle>
              <AlertDescription>{pwError}</AlertDescription>
            </Alert>
          )}
          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Mevcut Şifre</label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                autoComplete="current-password"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Yeni Şifre</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Yeni Şifre (Tekrar)</label>
              <input
                type="password"
                value={newPassword2}
                onChange={(e) => setNewPassword2(e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
                minLength={8}
                autoComplete="new-password"
              />
            </div>
            <Button type="submit" disabled={pwLoading}>
              {pwLoading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir'}
            </Button>
          </form>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
