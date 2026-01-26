'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert } from '@/components/ui/alert'
import { register } from '@/lib/auth'
import { formatError } from '@/lib/utils'

export default function RegisterPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }))
    setError('')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Validation
      if (!formData.username.trim()) {
        setError('Kullanıcı adı gereklidir')
        setLoading(false)
        return
      }
      if (!formData.email.trim()) {
        setError('E-posta gereklidir')
        setLoading(false)
        return
      }
      if (!formData.password) {
        setError('Şifre gereklidir')
        setLoading(false)
        return
      }
      if (formData.password !== formData.password_confirm) {
        setError('Şifreler eşleşmiyor')
        setLoading(false)
        return
      }
      if (formData.password.length < 8) {
        setError('Şifre en az 8 karakter olmalıdır')
        setLoading(false)
        return
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(formData.email)) {
        setError('Geçerli bir e-posta adresi girin')
        setLoading(false)
        return
      }

      // Register
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password2: formData.password_confirm,
        first_name: formData.first_name,
        last_name: formData.last_name,
      })

      // Redirect to login
      router.push('/login?registered=true')
    } catch (err) {
      setError(formatError(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-2">
          <CardTitle className="text-2xl">Hesap Oluştur</CardTitle>
          <CardDescription>
            Anka'ya kaydolun ve başlayın
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <div className="text-sm">{error}</div>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="username">Kullanıcı Adı</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="kullanıciadı"
                value={formData.username}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">E-posta</Label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="ornek@example.com"
                value={formData.email}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">Ad</Label>
                <Input
                  id="first_name"
                  name="first_name"
                  type="text"
                  placeholder="Ad"
                  value={formData.first_name}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="last_name">Soyadı</Label>
                <Input
                  id="last_name"
                  name="last_name"
                  type="text"
                  placeholder="Soyadı"
                  value={formData.last_name}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Şifre</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                required
              />
              <p className="text-xs text-gray-500">
                En az 8 karakter
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password_confirm">Şifreyi Onayla</Label>
              <Input
                id="password_confirm"
                name="password_confirm"
                type="password"
                placeholder="••••••••"
                value={formData.password_confirm}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Kaydolunuyor...' : 'Hesap Oluştur'}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              Zaten bir hesabınız var mı?{' '}
              <Link href="/login" className="font-medium text-blue-600 hover:text-blue-700">
                Giriş Yapın
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
