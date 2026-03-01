'use client'

import { Component, ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

/**
 * Global Error Boundary — catches unhandled React errors and shows
 * a friendly recovery UI instead of a blank white screen.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('[ErrorBoundary] Uncaught error:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="flex min-h-[50vh] items-center justify-center p-6">
          <Card className="max-w-md w-full">
            <CardHeader>
              <CardTitle className="text-red-600">Beklenmeyen Hata</CardTitle>
              <CardDescription>
                Bir şeyler ters gitti. Lütfen tekrar deneyin.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <pre className="text-xs bg-red-50 text-red-700 p-3 rounded-md overflow-auto max-h-40">
                  {this.state.error.message}
                </pre>
              )}
              <div className="flex gap-3">
                <Button variant="outline" onClick={this.handleReset}>
                  Tekrar Dene
                </Button>
                <Button onClick={this.handleReload}>
                  Sayfayı Yenile
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
