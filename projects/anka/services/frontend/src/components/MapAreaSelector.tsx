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
  const [drawingMode, setDrawingMode] = useState(!initialBounds)
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
    setDrawingMode(false)
    emitBounds(rect)
  }, [emitBounds])

  // ── DOM-event drawing (no deprecated drawing library) ──────────────────────
  const startDrawingMode = useCallback(() => {
    setDrawingMode(true)
  }, [])

  const clearRectangle = useCallback(() => {
    rectangleRef.current?.setMap(null)
    rectangleRef.current = null
    setHasRect(false)
    onBoundsChange(null)
    startDrawingMode()
  }, [onBoundsChange, startDrawingMode])

  // ── Pointer-event handlers as React props (avoids useEffect timing issues) ───
  // The overlay div is only rendered when ready && drawingMode, so these handlers
  // are guaranteed to be attached when the element exists. No useEffect needed.

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

    // Ignore tiny drags (< 8px)
    if (maxX - minX < 8 || maxY - minY < 8) return

    // Convert container pixels → LatLng using map viewport bounds.
    // Reliable alternative to MapCanvasProjection.fromContainerPixelToLatLng
    // which is unavailable when OverlayView.draw() hasn't been called (Maps API v3.60+).
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
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          {hasRect
            ? '✅ Arama alanı seçildi. Dörtgeni sürükleyip kenarlarından boyutlandırabilirsiniz.'
            : '✏️ Harita üzerinde tıklayıp sürükleyerek arama alanını çizin.'}
        </p>
        {hasRect && (
          <Button type="button" variant="outline" size="sm" onClick={clearRectangle}>
            Alanı Temizle
          </Button>
        )}
      </div>

      {/* Map container + transparent drawing overlay */}
      <div className="relative rounded-lg border border-input overflow-hidden" style={{ height, width: '100%' }}>
        {/* Google Maps canvas */}
        <div ref={mapRef} style={{ width: '100%', height: '100%' }} />

        {/* Transparent pointer-capture overlay — active only in drawing mode */}
        {ready && drawingMode && (
          <div
            ref={overlayDivRef}
            className="absolute inset-0"
            style={{ cursor: 'crosshair', zIndex: 10 }}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
          >
            {/* Live drag-rectangle feedback (pure CSS, no Maps API) */}
            <div
              ref={dragBoxRef}
              className="absolute pointer-events-none"
              style={{
                display: 'none',
                border: '2px solid #2563eb',
                backgroundColor: 'rgba(59,130,246,0.15)',
              }}
            />
          </div>
        )}
      </div>

      {!ready && !loadError && (
        <div
          className="absolute inset-0 flex items-center justify-center bg-muted/40 rounded-lg"
          style={{ position: 'relative', marginTop: `-${height}`, height }}
        >
          <p className="text-sm text-muted-foreground animate-pulse">Harita yükleniyor...</p>
        </div>
      )}
    </div>
  )
}
