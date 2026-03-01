'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
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
  /** Called whenever the user draws or edits the rectangle */
  onBoundsChange: (bounds: LocationBounds | null) => void
  /** Initial bounds (e.g. from an existing batch) */
  initialBounds?: LocationBounds | null
  /** Map height in CSS units */
  height?: string
}

const DEFAULT_CENTER = { lat: 39.0, lng: 35.0 }
const DEFAULT_ZOOM = 6

let googleMapsLoadPromise: Promise<void> | null = null

function loadGoogleMaps(apiKey: string): Promise<void> {
  if (googleMapsLoadPromise) return googleMapsLoadPromise

  if (window.google?.maps?.drawing) {
    return Promise.resolve()
  }

  setOptions({
    key: apiKey,
    v: 'weekly',
    libraries: ['drawing'],
  })

  googleMapsLoadPromise = Promise.all([
    importLibrary('maps'),
    importLibrary('drawing'),
  ]).then(() => undefined)

  return googleMapsLoadPromise
}

export default function MapAreaSelector({
  onBoundsChange,
  initialBounds,
  height = '420px',
}: MapAreaSelectorProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<google.maps.Map | null>(null)
  const rectangleRef = useRef<google.maps.Rectangle | null>(null)
  const drawingManagerRef = useRef<google.maps.drawing.DrawingManager | null>(null)
  const [ready, setReady] = useState(false)
  const [hasRect, setHasRect] = useState(!!initialBounds)
  const [loadError, setLoadError] = useState('')

  const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''

  const emitBounds = useCallback((rect: google.maps.Rectangle | null) => {
    if (!rect) {
      onBoundsChange(null)
      return
    }
    const b = rect.getBounds()!
    onBoundsChange({
      low: { latitude: b.getSouthWest().lat(), longitude: b.getSouthWest().lng() },
      high: { latitude: b.getNorthEast().lat(), longitude: b.getNorthEast().lng() },
    })
  }, [onBoundsChange])

  const placeRectangle = useCallback((map: google.maps.Map, bounds: google.maps.LatLngBounds) => {
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null)
    }

    const rect = new google.maps.Rectangle({
      bounds,
      map,
      editable: true,
      draggable: true,
      strokeColor: '#2563eb',
      strokeOpacity: 0.9,
      strokeWeight: 2,
      fillColor: '#3b82f6',
      fillOpacity: 0.15,
    })

    rect.addListener('bounds_changed', () => emitBounds(rect))
    rectangleRef.current = rect
    setHasRect(true)
    emitBounds(rect)

    if (drawingManagerRef.current) {
      drawingManagerRef.current.setDrawingMode(null)
    }
  }, [emitBounds])

  const clearRectangle = useCallback(() => {
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null)
      rectangleRef.current = null
    }
    setHasRect(false)
    onBoundsChange(null)
    if (drawingManagerRef.current) {
      drawingManagerRef.current.setDrawingMode(google.maps.drawing.OverlayType.RECTANGLE)
    }
  }, [onBoundsChange])

  useEffect(() => {
    if (!apiKey) {
      setLoadError('Google Maps API key tanımlı değil.')
      return
    }

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

        const drawingManager = new google.maps.drawing.DrawingManager({
          drawingMode: google.maps.drawing.OverlayType.RECTANGLE,
          drawingControl: false,
          rectangleOptions: {
            editable: true,
            draggable: true,
            strokeColor: '#2563eb',
            strokeOpacity: 0.9,
            strokeWeight: 2,
            fillColor: '#3b82f6',
            fillOpacity: 0.15,
          },
        })

        drawingManager.setMap(map)
        drawingManagerRef.current = drawingManager

        google.maps.event.addListener(drawingManager, 'rectanglecomplete', (rect: google.maps.Rectangle) => {
          rect.setMap(null)
          const bounds = rect.getBounds()!
          placeRectangle(map, bounds)
        })

        if (initialBounds) {
          const sw = new google.maps.LatLng(initialBounds.low.latitude, initialBounds.low.longitude)
          const ne = new google.maps.LatLng(initialBounds.high.latitude, initialBounds.high.longitude)
          const bounds = new google.maps.LatLngBounds(sw, ne)
          placeRectangle(map, bounds)
          map.fitBounds(bounds, 60)
          drawingManager.setDrawingMode(null)
        }

        setReady(true)
      })
      .catch((err) => {
        console.error('Google Maps load error:', err)
        setLoadError('Harita yüklenirken hata oluştu.')
      })

    return () => { cancelled = true }
  }, [apiKey, initialBounds, placeRectangle])

  if (loadError) {
    return (
      <div className="border-2 border-dashed border-red-300 rounded-lg flex items-center justify-center bg-red-50" style={{ height }}>
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
            : '🖱 Harita üzerinde dörtgen çizerek arama alanını belirleyin.'}
        </p>
        {hasRect && (
          <Button type="button" variant="outline" size="sm" onClick={clearRectangle}>
            Alanı Temizle
          </Button>
        )}
      </div>

      <div
        ref={mapRef}
        className="rounded-lg border border-input overflow-hidden"
        style={{ height, width: '100%' }}
      />

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
