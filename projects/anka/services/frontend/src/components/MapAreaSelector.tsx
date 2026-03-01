'use client'

import React, { useCallback, useEffect, useRef, useState } from 'react'
import { importLibrary, setOptions } from '@googlemaps/js-api-loader'
import { Button } from '@/components/ui/button'

/**
 * Bounds produced by the map rectangle drawing tool.
 * Matches Google Places API locationRestriction.rectangle format.
 */
export interface LocationBounds {
  low: { latitude: number; longitude: number }
  high: { latitude: number; longitude: number }
}

interface MapAreaSelectorProps {
  onBoundsChange: (bounds: LocationBounds | null) => void
  initialBounds?: LocationBounds | null
  height?: string
}

const DEFAULT_CENTER = { lat: 39.0, lng: 35.0 }
const DEFAULT_ZOOM = 6

const RECT_STYLE: google.maps.RectangleOptions = {
  editable: true,
  draggable: true,
  strokeColor: '#2563eb',
  strokeOpacity: 0.9,
  strokeWeight: 2,
  fillColor: '#3b82f6',
  fillOpacity: 0.15,
}

let googleMapsLoadPromise: Promise<void> | null = null

function loadGoogleMaps(apiKey: string): Promise<void> {
  if (googleMapsLoadPromise) return googleMapsLoadPromise

  if (window.google?.maps?.Map) {
    return Promise.resolve()
  }

  setOptions({ key: apiKey, v: 'weekly', libraries: ['maps'] })
  googleMapsLoadPromise = (importLibrary('maps') as Promise<any>).then(() => undefined)
  return googleMapsLoadPromise
}

interface DragState {
  startX: number
  startY: number
  currentX: number
  currentY: number
  active: boolean
}

export default function MapAreaSelector({
  onBoundsChange,
  initialBounds,
  height = '420px',
}: MapAreaSelectorProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const overlayDivRef = useRef<HTMLDivElement>(null)
  const dragBoxRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<google.maps.Map | null>(null)
  const rectangleRef = useRef<google.maps.Rectangle | null>(null)
  const dragRef = useRef<DragState | null>(null)

  const [ready, setReady] = useState(false)
  const [hasRect, setHasRect] = useState(!!initialBounds)
  // Harita her zaman pan edilebilir; kullanıcı "Alan Çiz" butonuna basınca drawing mode açılır
  const [drawingMode, setDrawingMode] = useState(false)
  const [loadError, setLoadError] = useState('')

  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''

  const emitBounds = useCallback((rect: google.maps.Rectangle | null) => {
    if (!rect) { onBoundsChange(null); return }
    const b = rect.getBounds()!
    onBoundsChange({
      low: { latitude: b.getSouthWest().lat(), longitude: b.getSouthWest().lng() },
      high: { latitude: b.getNorthEast().lat(), longitude: b.getNorthEast().lng() },
    })
  }, [onBoundsChange])

  const placeRectangle = useCallback((
    map: google.maps.Map,
    bounds: google.maps.LatLngBounds,
  ) => {
    rectangleRef.current?.setMap(null)
    const rect = new google.maps.Rectangle({ ...RECT_STYLE, bounds, map })
    rect.addListener('bounds_changed', () => emitBounds(rect))
    rectangleRef.current = rect
    setHasRect(true)
    setDrawingMode(false) // Çizim bitti → normal harita moduna dön
    emitBounds(rect)
  }, [emitBounds])

  const enterDrawingMode = useCallback(() => {
    setDrawingMode(true)
  }, [])

  const exitDrawingMode = useCallback(() => {
    setDrawingMode(false)
  }, [])

  const clearRectangle = useCallback(() => {
    rectangleRef.current?.setMap(null)
    rectangleRef.current = null
    setHasRect(false)
    setDrawingMode(false)
    onBoundsChange(null)
  }, [onBoundsChange])

  // ── Pointer-event handlers ────────────────────────────────────────────────
  // touch-action: none CSS ile birlikte kullanılır; iOS/Android'de harita
  // kaydırmasıyla çakışmayı önler. Overlay yalnızca drawingMode=true iken görünür.

  const handlePointerDown = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    e.preventDefault()
    const overlay = overlayDivRef.current
    const dragBox = dragBoxRef.current
    if (!overlay || !dragBox) return
    overlay.setPointerCapture(e.pointerId)
    const rect = overlay.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    dragRef.current = { startX: x, startY: y, currentX: x, currentY: y, active: true }
    dragBox.style.display = 'block'
    dragBox.style.left = `${x}px`
    dragBox.style.top = `${y}px`
    dragBox.style.width = '0px'
    dragBox.style.height = '0px'
  }, [])

  const handlePointerMove = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragRef.current?.active) return
    e.preventDefault()
    const overlay = overlayDivRef.current
    const dragBox = dragBoxRef.current
    if (!overlay || !dragBox) return
    const rect = overlay.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    dragRef.current.currentX = x
    dragRef.current.currentY = y
    const { startX, startY } = dragRef.current
    dragBox.style.left = `${Math.min(startX, x)}px`
    dragBox.style.top = `${Math.min(startY, y)}px`
    dragBox.style.width = `${Math.abs(x - startX)}px`
    dragBox.style.height = `${Math.abs(y - startY)}px`
  }, [])

  const handlePointerUp = useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!dragRef.current?.active) return
    const overlay = overlayDivRef.current
    const dragBox = dragBoxRef.current
    if (!overlay || !dragBox) return
    overlay.releasePointerCapture(e.pointerId)
    dragRef.current.active = false
    dragBox.style.display = 'none'

    const map = mapInstanceRef.current
    if (!map) return

    const { startX, startY, currentX, currentY } = dragRef.current
    const minX = Math.min(startX, currentX)
    const maxX = Math.max(startX, currentX)
    const minY = Math.min(startY, currentY)
    const maxY = Math.max(startY, currentY)

    // Çok küçük sürüklemeleri yok say (< 10px — mobilde parmak titremesi)
    if (maxX - minX < 10 || maxY - minY < 10) return

    const mapBounds = map.getBounds()
    const containerEl = mapRef.current
    if (!mapBounds || !containerEl) return

    const ne = mapBounds.getNorthEast()
    const sw = mapBounds.getSouthWest()
    const w = containerEl.offsetWidth || containerEl.getBoundingClientRect().width
    const h = containerEl.offsetHeight || containerEl.getBoundingClientRect().height
    if (!w || !h) return

    const toLat = (py: number) => ne.lat() - (py / h) * (ne.lat() - sw.lat())
    const toLng = (px: number) => sw.lng() + (px / w) * (ne.lng() - sw.lng())

    const swLatLng = new google.maps.LatLng(toLat(maxY), toLng(minX))
    const neLatLng = new google.maps.LatLng(toLat(minY), toLng(maxX))
    const bounds = new google.maps.LatLngBounds(swLatLng, neLatLng)
    placeRectangle(map, bounds)
  }, [placeRectangle])

  useEffect(() => {
    if (!apiKey) { setLoadError('Google Maps API key tanımlı değil.'); return }

    let cancelled = false

    loadGoogleMaps(apiKey)
      .then(() => {
        if (cancelled || !mapRef.current) return

        const map = new google.maps.Map(mapRef.current, {
          center: DEFAULT_CENTER,
          zoom: DEFAULT_ZOOM,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: true,
          // 'greedy': tek parmak ile pan, iki parmak ile zoom (mobil standart)
          gestureHandling: 'greedy',
          styles: [
            { featureType: 'poi', stylers: [{ visibility: 'off' }] },
            { featureType: 'transit', stylers: [{ visibility: 'off' }] },
          ],
        })
        mapInstanceRef.current = map

        if (initialBounds) {
          const sw = new google.maps.LatLng(initialBounds.low.latitude, initialBounds.low.longitude)
          const ne = new google.maps.LatLng(initialBounds.high.latitude, initialBounds.high.longitude)
          const bounds = new google.maps.LatLngBounds(sw, ne)
          placeRectangle(map, bounds)
          map.fitBounds(bounds, 60)
        }

        setReady(true)
      })
      .catch((err) => {
        console.error('Google Maps load error:', err)
        setLoadError('Harita yüklenirken hata oluştu.')
      })

    return () => { cancelled = true }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [apiKey])

  if (loadError) {
    return (
      <div
        className="border-2 border-dashed border-red-300 rounded-lg flex items-center justify-center bg-red-50"
        style={{ height }}
      >
        <p className="text-red-600 text-sm">{loadError}</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {/* ── Durum mesajı + aksiyonlar ── */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <p className="text-xs text-muted-foreground">
          {drawingMode
            ? '✏️ Parmağınızı haritaya basılı tutup sürükleyerek alan çizin.'
            : hasRect
              ? '✅ Arama alanı seçildi. Dörtgeni sürükleyip köşelerinden boyutlandırabilirsiniz.'
              : '📍 Önce haritada konumunuzu bulun, ardından "Alan Çiz" butonuna basın.'}
        </p>
        <div className="flex gap-2 shrink-0">
          {hasRect && !drawingMode && (
            <>
              <Button type="button" variant="outline" size="sm" onClick={enterDrawingMode}>
                Yeniden Çiz
              </Button>
              <Button type="button" variant="outline" size="sm" onClick={clearRectangle}>
                Alanı Sil
              </Button>
            </>
          )}
          {!hasRect && !drawingMode && ready && (
            <Button type="button" variant="default" size="sm" onClick={enterDrawingMode}>
              ✏️ Alan Çiz
            </Button>
          )}
          {drawingMode && (
            <Button type="button" variant="ghost" size="sm" onClick={exitDrawingMode}>
              İptal
            </Button>
          )}
        </div>
      </div>

      {/* ── Harita + çizim overlay ── */}
      <div className="relative rounded-lg border border-input overflow-hidden" style={{ height, width: '100%' }}>
        {/* Google Maps canvas — her zaman görünür ve etkileşimli */}
        <div ref={mapRef} style={{ width: '100%', height: '100%' }} />

        {/* Çizim overlay — YALNIZCA drawing mode açıkken gösterilir.
            touch-action:none iOS/Android harita pan'ını devre dışı bırakır
            ve pointer eventlerinin overlay'e gitmesini sağlar. */}
        {ready && drawingMode && (
          <>
            {/* Yarı saydam bilgi bandı */}
            <div
              className="absolute top-0 left-0 right-0 flex items-center justify-center gap-2 py-2 px-3"
              style={{
                background: 'rgba(37,99,235,0.88)',
                color: '#fff',
                fontSize: 13,
                fontWeight: 500,
                zIndex: 20,
                pointerEvents: 'none',
              }}
            >
              <span>👆 Parmağınızı basılı tutup sürükleyin</span>
            </div>

            {/* Şeffaf çizim alanı */}
            <div
              ref={overlayDivRef}
              className="absolute inset-0"
              style={{
                cursor: 'crosshair',
                zIndex: 10,
                touchAction: 'none', // ← Kritik: iOS/Android kaydırmasını engeller
              }}
              onPointerDown={handlePointerDown}
              onPointerMove={handlePointerMove}
              onPointerUp={handlePointerUp}
            >
              {/* Anlık seçim kutusu (CSS, Maps API yok) */}
              <div
                ref={dragBoxRef}
                className="absolute pointer-events-none"
                style={{
                  display: 'none',
                  border: '2px solid #2563eb',
                  backgroundColor: 'rgba(59,130,246,0.18)',
                  borderRadius: 2,
                }}
              />
            </div>
          </>
        )}

        {/* Yükleme göstergesi */}
        {!ready && !loadError && (
          <div className="absolute inset-0 flex items-center justify-center bg-muted/40">
            <p className="text-sm text-muted-foreground animate-pulse">Harita yükleniyor…</p>
          </div>
        )}
      </div>
    </div>
  )
}
