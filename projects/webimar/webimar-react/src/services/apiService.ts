/**
 * Backend API ile iletişim kurmak için servis fonksiyonları
 */
import { API_BASE_URL } from './api';

export interface CoordinateCheckRequest {
  lat: number;
  lng: number;
}

export interface CoordinateCheckResponse {
  inside_ova_polygons: string[];
  inside_yas_polygons: string[];
  province: string | null;
  district: string | null;
  lat: number;
  lng: number;
  total_ova_polygons: number;
  total_yas_polygons: number;
  total_provinces: number;
  total_districts: number;
  // Backward compatibility fields from older API versions
  inside_polygons?: string[];
  inside_kapali_alan_polygons?: string[];
  in_yas_kapali_alan?: boolean;
}

export interface ApiError {
  error: string;
}

/**
 * Koordinat doğrulama API'sini çağırır
 */
export const checkCoordinate = async (
  lat: number,
  lng: number
): Promise<CoordinateCheckResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/maps/check-coordinate/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ lat, lng }),
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data: CoordinateCheckResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Coordinate check API error:', error);
    throw error;
  }
};

/**
 * Backend API sağlık kontrolü
 */
export const healthCheck = async (): Promise<{ status: string; message?: string; app?: string; detail?: string }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/maps/health/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check API error:', error);
    throw error;
  }
};
