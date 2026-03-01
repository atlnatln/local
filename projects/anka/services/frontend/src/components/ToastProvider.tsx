'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'

export type ToastVariant = 'default' | 'success' | 'error' | 'warning'

interface Toast {
  id: string
  message: string
  variant: ToastVariant
}

interface ToastContextValue {
  toasts: Toast[]
  addToast: (message: string, variant?: ToastVariant) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

let _nextId = 0

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const addToast = useCallback(
    (message: string, variant: ToastVariant = 'default') => {
      const id = `toast-${++_nextId}`
      setToasts(prev => [...prev, { id, message, variant }])
      // Auto-dismiss after 4 seconds
      setTimeout(() => removeToast(id), 4000)
    },
    [removeToast],
  )

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      {/* Toast container — fixed bottom-right */}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
        {toasts.map(toast => (
          <div
            key={toast.id}
            className={`
              pointer-events-auto rounded-lg shadow-lg px-4 py-3 text-sm font-medium
              animate-in slide-in-from-right-5 fade-in duration-200
              ${variantClasses[toast.variant]}
            `}
          >
            <div className="flex items-center justify-between gap-2">
              <span>{toast.message}</span>
              <button
                onClick={() => removeToast(toast.id)}
                className="ml-2 opacity-60 hover:opacity-100 text-current"
              >
                &times;
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

const variantClasses: Record<ToastVariant, string> = {
  default: 'bg-white border border-gray-200 text-gray-900',
  success: 'bg-green-600 text-white',
  error: 'bg-red-600 text-white',
  warning: 'bg-amber-500 text-white',
}
