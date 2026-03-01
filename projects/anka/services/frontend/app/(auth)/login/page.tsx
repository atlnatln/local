'use client'

import { useEffect, useState, useCallback, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
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
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Read redirect target from query string (set by middleware)
  // Validate redirect to prevent open-redirect attacks — only allow relative paths
  const rawRedirect = searchParams.get('redirect') || '/dashboard'
  const redirectTo = rawRedirect.startsWith('/') && !rawRedirect.startsWith('//') ? rawRedirect : '/dashboard'
  // Ref to avoid stale closure with redirectTo
  const redirectRef = useRef(redirectTo)
  redirectRef.current = redirectTo

  const handleGoogleCallback = useCallback(async (response: { credential?: string }) => {
    if (!response?.credential) {
      setError('Google oturum yanıtı alınamadı.')
      return
    }

    setLoading(true)
    setError('')
    try {
      await loginWithGoogleIdToken(response.credential)
      router.push(redirectRef.current)
    } catch (err) {
      setError(formatError(err))
      console.error('Google login error:', err)
    } finally {
      setLoading(false)
    }
  }, [router])

  useEffect(() => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID
    if (!clientId) {
      setError('Google Client ID ayarlı değil (NEXT_PUBLIC_GOOGLE_CLIENT_ID).')
      return
    }

    function initGoogleButton() {
      if (!window.google?.accounts?.id) return

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleGoogleCallback,
      })

      window.google.accounts.id.renderButton(
        document.getElementById('googleSignInButton'),
        { theme: 'outline', size: 'large', width: 'auto' }
      )
    }

    // If script already loaded, just re-init
    const existing = document.getElementById('google-identity-services') as HTMLScriptElement | null
    if (existing && window.google?.accounts?.id) {
      initGoogleButton()
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
      initGoogleButton()
    }

    script.onerror = () => {
      setError('Google giriş servisi yüklenemedi (network).')
    }

    document.head.appendChild(script)

    // Cleanup: remove script on unmount to prevent duplicates
    return () => {
      if (script.parentNode) {
        script.parentNode.removeChild(script)
      }
    }
  }, [handleGoogleCallback])

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

          {error && error.includes('yüklenemedi') && (
            <Button
              type="button"
              variant="outline"
              className="w-full"
              onClick={() => {
                setError('')
                window.location.reload()
              }}
            >
              Tekrar Dene
            </Button>
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
