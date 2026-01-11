// KML to GeoJSON conversion utilities for React Leaflet
import L from 'leaflet';

export interface KMLLayerConfig {
  name: string;
  url: string;
  style?: {
    color?: string;
    weight?: number;
    fillColor?: string;
    fillOpacity?: number;
    opacity?: number;
  };
  visible?: boolean;
}

export interface ParsedKMLLayer {
  name: string;
  geoJson: any;
  style: any;
  bounds?: L.LatLngBounds;
}

export class KMLParser {
  /**
   * Parse KML string to GeoJSON
   */
  static parseKMLToGeoJSON(kmlString: string): any {
    const parser = new DOMParser();
    const kmlDoc = parser.parseFromString(kmlString, 'text/xml');
    
    // Simple KML to GeoJSON conversion
    // In a production environment, you'd use a more robust library
    const features: any[] = [];
    
    // Parse Placemarks
    const placemarks = kmlDoc.getElementsByTagName('Placemark');
    for (let i = 0; i < placemarks.length; i++) {
      const placemark = placemarks[i];
      const feature = this.parseFeature(placemark);
      if (feature) {
        features.push(feature);
      }
    }
    
    return {
      type: 'FeatureCollection',
      features: features
    };
  }
  
  /**
   * Parse individual KML feature
   */
  private static parseFeature(placemark: Element): any {
    const name = placemark.getElementsByTagName('name')[0]?.textContent || '';
    const description = placemark.getElementsByTagName('description')[0]?.textContent || '';
    
    // Parse geometry
    const polygon = placemark.getElementsByTagName('Polygon')[0];
    const point = placemark.getElementsByTagName('Point')[0];
    const lineString = placemark.getElementsByTagName('LineString')[0];
    
    let geometry = null;
    
    if (polygon) {
      geometry = this.parsePolygon(polygon);
    } else if (point) {
      geometry = this.parsePoint(point);
    } else if (lineString) {
      geometry = this.parseLineString(lineString);
    }
    
    if (!geometry) return null;
    
    return {
      type: 'Feature',
      properties: {
        name: name,
        description: description
      },
      geometry: geometry
    };
  }
  
  /**
   * Parse KML Polygon to GeoJSON
   */
  private static parsePolygon(polygon: Element): any {
    const outerBoundary = polygon.getElementsByTagName('outerBoundaryIs')[0];
    if (!outerBoundary) return null;
    
    const linearRing = outerBoundary.getElementsByTagName('LinearRing')[0];
    if (!linearRing) return null;
    
    const coordinates = linearRing.getElementsByTagName('coordinates')[0];
    if (!coordinates) return null;
    
    const coordString = coordinates.textContent?.trim();
    if (!coordString) return null;
    
    const coords = this.parseCoordinateString(coordString);
    
    return {
      type: 'Polygon',
      coordinates: [coords]
    };
  }
  
  /**
   * Parse KML Point to GeoJSON
   */
  private static parsePoint(point: Element): any {
    const coordinates = point.getElementsByTagName('coordinates')[0];
    if (!coordinates) return null;
    
    const coordString = coordinates.textContent?.trim();
    if (!coordString) return null;
    
    const coord = this.parseCoordinateString(coordString)[0];
    
    return {
      type: 'Point',
      coordinates: coord
    };
  }
  
  /**
   * Parse KML LineString to GeoJSON
   */
  private static parseLineString(lineString: Element): any {
    const coordinates = lineString.getElementsByTagName('coordinates')[0];
    if (!coordinates) return null;
    
    const coordString = coordinates.textContent?.trim();
    if (!coordString) return null;
    
    const coords = this.parseCoordinateString(coordString);
    
    return {
      type: 'LineString',
      coordinates: coords
    };
  }
  
  /**
   * Parse coordinate string from KML
   */
  private static parseCoordinateString(coordString: string): number[][] {
    return coordString
      .split(/\s+/)
      .filter(coord => coord.trim())
      .map(coord => {
        const parts = coord.split(',');
        return [
          parseFloat(parts[0]), // longitude
          parseFloat(parts[1]), // latitude
          parts[2] ? parseFloat(parts[2]) : 0 // altitude (optional)
        ];
      });
  }
}

export class KMLLoader {
  /**
   * Load KML file from URL and convert to GeoJSON
   */
  static async loadKMLLayer(config: KMLLayerConfig): Promise<ParsedKMLLayer> {
    try {
      const response = await fetch(config.url);
      if (!response.ok) {
        throw new Error(`Failed to load KML: ${response.statusText}`);
      }
      
      const kmlString = await response.text();
      const geoJson = KMLParser.parseKMLToGeoJSON(kmlString);
      
      // Calculate bounds if features exist
      let bounds: L.LatLngBounds | undefined;
      if (geoJson.features && geoJson.features.length > 0) {
        const layer = L.geoJSON(geoJson);
        bounds = layer.getBounds();
      }
      
      return {
        name: config.name,
        geoJson: geoJson,
        style: config.style || {},
        bounds: bounds
      };
    } catch (error) {
      console.error(`Error loading KML layer ${config.name}:`, error);
      throw error;
    }
  }
  
  /**
   * Load multiple KML layers
   */
  static async loadKMLLayers(configs: KMLLayerConfig[]): Promise<ParsedKMLLayer[]> {
    const promises = configs.map(config => this.loadKMLLayer(config));
    return Promise.all(promises);
  }
}

// Default KML layer configurations for webimar (matching original system)
export const DEFAULT_KML_LAYERS: KMLLayerConfig[] = [
  {
    name: 'İzmir Sınırları',
    url: '/static/izmir.kml',
    style: {
      color: '#006600',
      weight: 3,
      fillOpacity: 0.05
    },
    visible: true
  },
  {
    name: 'İzmir Kapalı Alanlar',
    url: '/static/izmir_kapali_alan.kml',
    style: {
      color: 'red',
      weight: 0,
      fillOpacity: 0,
      fillColor: 'red'
    },
    visible: true
  },
  {
    name: 'Büyük Ovalar İzmir',
    url: '/static/Büyük Ovalar İzmir.kml',
    style: {
      color: 'blue',
      weight: 0,
      fillOpacity: 0.0
    },
    visible: true
  }
];
