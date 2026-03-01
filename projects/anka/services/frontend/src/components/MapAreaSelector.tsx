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

const RECT_STYLE = {
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

  setOptions({
    key: apiKey,
    v: 'weekly',
    libraries: ['maps'],
  })

  googleMapsLoadPromise = importLibrary('maps').then(() => undefined)

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
  const drawingListenersRef = useRef<google.maps.MapsEventListener[]>([])
  const isDrawingRef = useRef(false)
  const drawStartRef = useRef<google.maps.LatLng | null>(null)
  const tempRectRef = useRef<google.maps.Rectangle | null>(null)
  const [ready, setReady] = useState(false)
  const [hasRect, setHasRect] = useState(!!initialBounds)
  const [loadError, setLoadError] = useState('')
  const [drawingMode, setDrawingMode] = useState(!initialBounds)

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
      ...RECT_STYLE,
      bounds,
      map,
    })

    rect.addListener('bounds_changed', () => emitBounds(rect))
    rectangleRef.current = rect
    setHasRect(true)
    setDrawingMode(false)
    emitBounds(rect)

    // Re-enable map panning
    map.setOptions({ draggable: true, gestureHandling: 'greedy' })
  }, [emitBounds])

  const removeDrawingListeners = useCallback(() => {
    drawingListenersRef.current.forEach(l => google.maps.event.removeListener(l))
    drawingListenersRef.current = []
  }, [])

  const enableDrawingMode = useCallback((map: google.maps.Map) => {
    removeDrawingListeners()
    map.setOptions({ draggable: false, gestureHandling: 'none', cursor: 'crosshair' })
    isDrawingRef.current = false
    drawStartRef.current = null

    const onMouseDown = map.addListener('mousedown', (e: google.maps.MapMouseEvent) => {
      if (!e.latLng) return
      isDrawingRef.current = true
      drawStartRef.current = e.latLng
      if (tempRectRef.current) {
        tempRectRef.current.setMap(null)
        tempRectRef.current = null
      }
      tempRectRef.current = new google.maps.Rectangle({
        ...RECT_STYLE,
        editable: false,
        draggable: false,
        bounds: { north: e.latLng.lat(), south: e.latLng.lat(), east: e.latLng.lng(), west: e.latLng.lng() },
        map,
      })
    })

    const onMouseMove = map.addListener('mousemove', (e: google.maps.MapMouseEvent) => {
      if (!isDrawingRef.current || !drawStartRef.current || !tempRectRef.current || !e.latLng) return
      const s = drawStartRef.current
      const c = e.latLng
      tempRectRef.current.setBounds({
        north: Math.max(s.lat(), c.lat()),
        south: Math.min(s.lat(), c.lat()),
        east: Math.max(s.lng(), c.lng()),
        west: Math.min(s.lng(), c.lng()),
      })
    })

    const onMouseUp = map.addListener('mouseup', (e: google.maps.MapMouseEvent) => {
      if (!isDrawingRef.current || !drawStartRef.current) return
      isDrawingRef.current = false
      if (tempRectRef.current) {
        const bounds = tempRectRef.current.getBounds()
        tempRectRef.current.setMap(null)
        tempRectRef.current = null
        if (bounds) {
          removeDrawingListeners()
          map.setOptions({ cursor: '' })
          placeRectangle(map, bounds)
        }
      }
    })

    drawingListenersRef.current = [onMouseDown, onMouseMove, onMouseUp]
  }, [placeRectangle, removeDrawingListeners])

  const clearRectangle = useCallback(() => {
    if (rectangleRef.current) {
      rectangleRef.current.setMap(null)
      rectangleRef.current = null
    }
    setHasRect(false)
    setDrawingMode(true)
    onBoundsChange(null)
    if (mapInstanceRef.current) {
      enableDrawingMode(mapInstanceRef.current)
    }
  }, [onBoundsChange, enableDrawingMode])

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

        if (initialBounds) {
          const sw = new google.maps.LatLng(initialBounds.low.latitude, initialBounds.low.longitude)
          const ne = new google.maps.LatLng(initialBounds.high.latitude, initialBounds.high.longitude)
          const bounds = new google.maps.LatLngBounds(sw, ne)
          placeRectangle(map, bounds)
          map.fitBounds(bounds, 60)
        } else {
          enableDrawingMode(map)
        }

        setReady(true)
      })
      .catch((err) => {
        console.error('Google Maps load error:', err)
        setLoadError('Harita yüklenirken hata oluştu.')
      })

    return () => {
      cancelled = true
      removeDrawingListeners()
    }
  }, [apiKey, initialBounds, placeRectangle, enableDrawingMode, removeDrawingListeners])

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
            : drawingMode
              ? '✏️ Harita üzerinde tıklayıp sürükleyerek arama alanını çizin.'
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
