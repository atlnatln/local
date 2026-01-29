import json
import logging
import math
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict

logger = logging.getLogger(__name__)

@dataclass
class Point:
    lat: float
    lng: float

@dataclass
class Rectangle:
    low: Point
    high: Point
    
    def to_dict(self):
        return {
            "rectangle": {
                "low": {"latitude": self.low.lat, "longitude": self.low.lng},
                "high": {"latitude": self.high.lat, "longitude": self.high.lng}
            }
        }

    def split(self) -> List['Rectangle']:
        """
        Divides the rectangle into 4 smaller quadrants (NW, NE, SW, SE).
        """
        mid_lat = (self.low.lat + self.high.lat) / 2.0
        mid_lng = (self.low.lng + self.high.lng) / 2.0
        
        # 1. South-West
        sw = Rectangle(
            low=self.low,
            high=Point(mid_lat, mid_lng)
        )
        # 2. South-East
        se = Rectangle(
            low=Point(self.low.lat, mid_lng),
            high=Point(mid_lat, self.high.lng)
        )
        # 3. North-West
        nw = Rectangle(
            low=Point(mid_lat, self.low.lng),
            high=Point(self.high.lat, mid_lng)
        )
        # 4. North-East
        ne = Rectangle(
            low=Point(mid_lat, mid_lng),
            high=self.high
        )
        return [sw, se, nw, ne]

class GridSearch:
    def __init__(self, geojson_path: str = None):
        if geojson_path is None:
            # Resolve relative to this file to be robust regardless of CWD
            base_path = os.path.dirname(os.path.abspath(__file__))
            # Go up levels: apps/providers -> apps -> backend -> services -> ROOT
            # actually structure is: services/backend/apps/providers/grid_search.py
            # we need: docs/turkey-districts.geojson
            # ../../../../docs/turkey-districts.geojson
            
            # Helper to find project root approx
            root = base_path
            for _ in range(4): # providers, apps, backend, services
                root = os.path.dirname(root)
            
            geojson_path = os.path.join(root, 'docs', 'turkey-districts.geojson')
            
        # Fallback if calculated path doesn't exist (maybe dev env difference)
        if not os.path.exists(geojson_path):
             # Try simple relative if running from backend root
             candidate = os.path.join('..', '..', 'docs', 'turkey-districts.geojson')
             if os.path.exists(candidate):
                 geojson_path = candidate

        self.geojson_path = geojson_path
        self._feature_collection = None
        
        if not os.path.exists(self.geojson_path):
            logger.warning(f"GeoJSON file not found at {self.geojson_path}. Grid Search will not work.")
        # Adjust path as needed relative to where this code runs
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        self.geojson_path = os.path.join(base_dir, geojson_path)
        self.features = []
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.geojson_path):
            logger.warning(f"GeoJSON file not found at {self.geojson_path}")
            return
            
        try:
            with open(self.geojson_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.features = data.get('features', [])
        except Exception as e:
            logger.error(f"Failed to load GeoJSON: {e}")

    def get_bounding_box(self, city: str, district: str = None) -> Optional[Rectangle]:
        """
        Get the overall bounding box for a city or district.
        Returns a single Rectangle that encompasses the entire area.
        """
        feature = self.find_boundary(city, district)
        if not feature:
            return None
            
        geometry = feature.get('geometry')
        if not geometry:
            return None
            
        coords = self._extract_coordinates(geometry)
        if not coords:
            return None
            
        # Calculate bounding box
        lats = [coord[1] for coord in coords]
        lngs = [coord[0] for coord in coords]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        return Rectangle(
            low=Point(min_lat, min_lng),
            high=Point(max_lat, max_lng)
        )

    def find_boundary(self, city: str, district: Optional[str] = None) -> Optional[dict]:
        """
        Finds the GeoJSON feature for a given city and optional district.
        """
        if not self.features:
            self._load_data()
            
        normalized_city = self._normalize(city)
        normalized_district = self._normalize(district) if district else None
        
        target_features = []
        
        for feature in self.features:
            props = feature.get('properties', {})
            feat_city = self._normalize(props.get('ADM1_TR') or props.get('ADM1_EN'))
            feat_district = self._normalize(props.get('ADM2_TR') or props.get('ADM2_EN'))
            
            if feat_city == normalized_city:
                if normalized_district:
                    if feat_district == normalized_district:
                        return feature # Exact match
                else:
                    target_features.append(feature) # Accumulate all districts if only city is given
        
        if not normalized_district and target_features:
            # If we want the whole city, we might need to merge bboxes or just return one specific logic.
            # For simplicity, let's return a merged bounding box feature or the MultiPolygon of the province if available.
            # However, looking at the file structure, it seems split by districts.
            # A simple approach: Compute union bbox of all districts.
            return self._merge_features(target_features)
            
        return None

    def _normalize(self, text: str) -> str:
        if not text:
            return ""
        import unicodedata
        return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').upper()

    def _merge_features(self, features: List[dict]) -> dict:
        """
        Creates a virtual feature that envelops all provided features (bbox union).
        """
        if not features:
            return None
            
        # Initialize with first feature's bbox logic
        min_lng, min_lat = 180, 90
        max_lng, max_lat = -180, -90
        
        for feat in features:
            coords = self._extract_coordinates(feat)
            for lng, lat in coords:
                min_lng = min(min_lng, lng)
                max_lng = max(max_lng, lng)
                min_lat = min(min_lat, lat)
                max_lat = max(max_lat, lat)
                
        # Construct a simple bbox polygon feature
        return {
            "type": "Feature",
            "bbox": [min_lng, min_lat, max_lng, max_lat], # Standard GeoJSON bbox
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [min_lng, min_lat],
                    [min_lng, max_lat],
                    [max_lng, max_lat],
                    [max_lng, min_lat],
                    [min_lng, min_lat]
                ]]
            },
            "properties": {"name": "Merged Feature"}
        }

    def _extract_coordinates(self, feature: dict) -> List[Tuple[float, float]]:
        """
        Flatten coordinates from Polygon or MultiPolygon.
        Handles both GeoJSON features and simple geometry objects.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"🔍 Feature keys: {list(feature.keys())}")
        logger.debug(f"🔍 Feature content: {feature}")
        
        geoms = []
        
        # Check if it's a GeoJSON feature with geometry field
        if 'geometry' in feature:
            geom = feature['geometry']
            if geom['type'] == 'Polygon':
                geoms.append(geom['coordinates'])
            elif geom['type'] == 'MultiPolygon':
                geoms = geom['coordinates']
        # Handle simple geometry objects (like bounding boxes)
        elif 'type' in feature and 'coordinates' in feature:
            if feature['type'] == 'Polygon':
                geoms.append(feature['coordinates'])
            elif feature['type'] == 'MultiPolygon':
                geoms = feature['coordinates']
        else:
            logger.warning(f"🚨 Unknown feature format: {feature}")
            return []
            
        all_coords = []
        for poly in geoms:
            for ring in poly:
                for coord in ring:
                    all_coords.append(tuple(coord))
        return all_coords

    def generate_grids(self, boundary_feature: dict, grid_step_km: float = 2.0) -> List[Rectangle]:
        """
        Generates a list of rectangular viewports covering the feature's bounding box.
        
        Args:
            boundary_feature: The GeoJSON feature to cover.
            grid_step_km: The side length of each grid square in kilometers.
        """
        coords = self._extract_coordinates(boundary_feature)
        lats = [c[1] for c in coords]
        lngs = [c[0] for c in coords]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        
        # Approximate conversion degrees to km
        # 1 deg lat ~= 111 km
        # 1 deg lng ~= 111 * cos(lat) km
        
        lat_step = grid_step_km / 111.0
        avg_lat = (min_lat + max_lat) / 2.0
        lng_step = grid_step_km / (111.0 * math.cos(math.radians(avg_lat)))
        
        grids = []
        
        curr_lat = min_lat
        while curr_lat < max_lat:
            curr_lng = min_lng
            while curr_lng < max_lng:
                # Create rectangle
                low = Point(curr_lat, curr_lng)
                high = Point(min(curr_lat + lat_step, max_lat), min(curr_lng + lng_step, max_lng))
                
                rect = Rectangle(low, high)
                
                # Optimization: Check if rectangle center is crudely roughly inside/near polygon?
                # For now, just returning all tiles in bbox (simple bounding box tiling).
                # This ensures 100% coverage, even if efficiency is lower than polygon-clipped.
                grids.append(rect)
                
                curr_lng += lng_step
            curr_lat += lat_step
            
        return grids

# Adaptive Search Functions
def get_adaptive_search_regions(city: str, district: str = None) -> Optional[Rectangle]:
    """
    Get the starting bounding box for adaptive quadtree search.
    Returns the overall city/district boundary as a single rectangle.
    """
    searcher = GridSearch()
    return searcher.get_bounding_box(city, district)

def get_search_grids(city: str, district: str = None, grid_step_km: float = 5.0) -> List[dict]:
    """
    Helper to get API-ready locationRestriction objects.
    Default grid step bumped to 5km to avoid too many requests for MVP.
    This is the OLD method - kept for backward compatibility.
    """
    searcher = GridSearch()
    feature = searcher.find_boundary(city, district)
    
    if not feature:
        # Fallback: if not found, we can't restrict safely. Return empty or better handling?
        # Maybe handle in caller.
        return []
        
    rects = searcher.generate_grids(feature, grid_step_km)
    return [r.to_dict() for r in rects]
