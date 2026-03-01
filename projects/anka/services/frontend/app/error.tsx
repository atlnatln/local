'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Unhandled application error:', error)
  }, [error])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-6">
      <div className="text-center max-w-md space-y-6">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <svg
            className="h-8 w-8 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h2 className="text-2xl font-semibold text-gray-900">
          Beklenmeyen Bir Hata Oluştu
        </h2>
        <p className="text-gray-600">
          Bir şeyler ters gitti. Lütfen tekrar deneyin veya sorun devam ederse
          destek ekibiyle iletişime geçin.
        </p>
        {error.digest && (
          <p className="text-xs text-gray-400 font-mono">
            Hata kodu: {error.digest}
          </p>
        )}
        <div className="flex gap-3 justify-center">
          <Button onClick={reset}>Tekrar Dene</Button>
          <Button
            variant="outline"
            onClick={() => (window.location.href = '/dashboard')}
          >
            Dashboard&apos;a Dön
          </Button>
        </div>
      </div>
    </div>
  )
}
