'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { loginWithGoogleIdToken } from '@/lib/auth'
import { formatError } from '@/lib/utils'

declare global {
  interface Window {
    google?: any
  }
}

export default function LoginPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
    if (!clientId) {
      setError('Google Client ID ayarlı değil (NEXT_PUBLIC_GOOGLE_CLIENT_ID).')
      return
    }

    const existing = document.getElementById('google-identity-services') as HTMLScriptElement | null
    if (existing && window.google?.accounts?.id) {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response: { credential?: string }) => {
          if (!response?.credential) {
            setError('Google oturum yanıtı alınamadı.')
            return
          }

          setLoading(true)
          setError('')
          try {
            await loginWithGoogleIdToken(response.credential)
            router.push('/dashboard')
          } catch (err) {
            setError(formatError(err))
            console.error('Google login error:', err)
          } finally {
            setLoading(false)
          }
        },
      })

      window.google.accounts.id.renderButton(
        document.getElementById('googleSignInButton'),
        { theme: 'outline', size: 'large', width: 400 }
      )
      return
    }

    const script = document.createElement('script')
    script.id = 'google-identity-services'
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true

    script.onload = () => {
      if (!window.google?.accounts?.id) {
        setError('Google giriş servisi yüklenemedi.')
        return
      }

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response: { credential?: string }) => {
          if (!response?.credential) {
            setError('Google oturum yanıtı alınamadı.')
            return
          }

          setLoading(true)
          setError('')
          try {
            await loginWithGoogleIdToken(response.credential)
            router.push('/dashboard')
          } catch (err) {
            setError(formatError(err))
            console.error('Google login error:', err)
          } finally {
            setLoading(false)
          }
        },
      })

      window.google.accounts.id.renderButton(
        document.getElementById('googleSignInButton'),
        { theme: 'outline', size: 'large', width: 400 }
      )
    }

    script.onerror = () => {
      setError('Google giriş servisi yüklenemedi (network).')
    }

    document.head.appendChild(script)
  }, [router])

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="space-y-1">
        <CardTitle className="text-center text-2xl">Anka Platform</CardTitle>
        <CardDescription className="text-center">Giriş Yap</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {error && (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <div id="googleSignInButton" className="w-full" />

          <Button type="button" className="w-full" disabled>
            {loading ? 'Giriş yapılıyor...' : 'Sadece Google ile giriş yapılır'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
