"""
Google Maps Search Results Management Service
Sektör standardında arama sonuçları kaydetme, yönetme ve zenginleştirme sistemi
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
from django.conf import settings
from django.contrib.auth.models import User
from apps.records.models import SearchQuery, BusinessCandidate, EnrichmentLog
from apps.accounts.models import Organization
from django.utils import timezone


class GoogleMapsResultsManager:
    """Google Maps API sonuçlarını kaydetme ve yönetme sistemi"""
    
    def __init__(self, user_identifier: str, organization: Organization = None):
        self.user_identifier = user_identifier
        self.organization = organization or self._get_default_org()
        self.user = self._get_user()
        
        # Dosya kayıt dizinleri
        self.base_dir = Path(settings.BASE_DIR) / 'data' / 'google_maps_searches'
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_default_org(self) -> Organization:
        """Varsayılan organizasyonu al veya oluştur"""
        org, _ = Organization.objects.get_or_create(
            name="Default Organization",
            defaults={'description': 'Auto-created for searches'}
        )
        return org
    
    def _get_user(self) -> Optional[User]:
        """Kullanıcıyı username ile bul"""
        try:
            return User.objects.get(username=self.user_identifier)
        except User.DoesNotExist:
            return None
    
    def create_search_query(
        self,
        query_text: str,
        city: str,
        sector: str,
        max_stage: str = 'stage3',
        location_bias: Optional[Dict] = None
    ) -> SearchQuery:
        """Yeni bir arama sorgusu oluştur"""
        
        search_query = SearchQuery.objects.create(
            organization=self.organization,
            created_by=self.user_identifier,
            user=self.user,
            query_text=query_text,
            city=city,
            sector=sector,
            max_stage=max_stage,
            location_bias=location_bias or {},
            status='pending'
        )
        
        # Dosya dizini oluştur
        query_dir = self.base_dir / f"query_{search_query.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        query_dir.mkdir(parents=True, exist_ok=True)
        
        return search_query
    
    def save_raw_results(
        self,
        search_query: SearchQuery,
        stage1_results: List[Dict] = None,
        stage2_results: List[Dict] = None,
        stage3_results: List[Dict] = None,
        api_call_stats: Dict = None
    ) -> str:
        """Ham API sonuçlarını dosyaya kaydet"""
        
        # Dosya yolu
        query_dir = self.base_dir / f"query_{search_query.id}_{search_query.created_at.strftime('%Y%m%d_%H%M%S')}"
        query_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = query_dir / "raw_results.json"
        
        # Ham veriler
        raw_data = {
            'search_query': {
                'id': search_query.id,
                'query_text': search_query.query_text,
                'city': search_query.city,
                'sector': search_query.sector,
                'max_stage': search_query.max_stage,
                'created_by': search_query.created_by,
                'organization': search_query.organization.name,
                'created_at': search_query.created_at.isoformat()
            },
            'api_calls': api_call_stats or {},
            'results': {
                'stage1': stage1_results or [],
                'stage2': stage2_results or [],
                'stage3': stage3_results or []
            },
            'metadata': {
                'total_candidates': len(stage3_results or stage2_results or stage1_results or []),
                'exported_at': timezone.now().isoformat(),
                'export_version': '1.0'
            }
        }
        
        # JSON olarak kaydet
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        # Dosya yolunu search_query'ye kaydet
        search_query.raw_results_file = str(raw_file)
        search_query.save()
        
        return str(raw_file)
    
    def save_candidates_to_db(
        self,
        search_query: SearchQuery,
        candidates: List[Dict],
        stage: str = 'stage3'
    ) -> List[BusinessCandidate]:
        """Adayları veritabanına kaydet"""
        
        saved_candidates = []
        
        for candidate_data in candidates:
            place_id = candidate_data.get('id') or candidate_data.get('place_id')
            if not place_id:
                continue
                
            # Mevcut adayı kontrol et
            existing = BusinessCandidate.objects.filter(place_id=place_id).first()
            if existing:
                # Güncelle
                candidate = existing
                candidate.search_query = search_query  # En son sorguya bağla
            else:
                # Yeni oluştur
                candidate = BusinessCandidate(
                    search_query=search_query,
                    place_id=place_id
                )
            
            # Temel bilgileri güncelle
            candidate.name = candidate_data.get('name', candidate_data.get('displayName', ''))
            candidate.formatted_address = candidate_data.get('address', candidate_data.get('formattedAddress', ''))
            candidate.place_types = candidate_data.get('types', [])
            candidate.business_status = candidate_data.get('businessStatus', 'UNKNOWN')
            
            # Konum bilgileri
            if 'location' in candidate_data:
                location = candidate_data['location']
                candidate.latitude = location.get('latitude')
                candidate.longitude = location.get('longitude')
            
            # Rating bilgileri
            candidate.rating = candidate_data.get('rating')
            candidate.user_ratings_total = candidate_data.get('userRatingCount')
            
            # İletişim bilgileri (Stage 3'te gelir)
            if stage == 'stage3':
                candidate.website = candidate_data.get('website')
                candidate.phone_number = candidate_data.get('phone')
                candidate.international_phone = candidate_data.get('internationalPhoneNumber')
                candidate.last_enriched_stage = 'stage3'
                candidate.verification_status = 'enriched'
            elif stage == 'stage2':
                candidate.last_enriched_stage = 'stage2'
                candidate.verification_status = 'verified'
                candidate.verification_reason = candidate_data.get('verification_reason', 'stage2_verified')
            
            # Stage bilgisi
            if not candidate.collected_at_stage:
                candidate.collected_at_stage = stage
            
            candidate.save()
            saved_candidates.append(candidate)
        
        return saved_candidates
    
    def export_to_csv(self, search_query: SearchQuery) -> str:
        """Sonuçları CSV olarak dışa aktar"""
        import csv
        
        query_dir = self.base_dir / f"query_{search_query.id}_{search_query.created_at.strftime('%Y%m%d_%H%M%S')}"
        query_dir.mkdir(parents=True, exist_ok=True)
        
        csv_file = query_dir / "results.csv"
        
        candidates = search_query.candidates.all()
        
        # CSV başlıkları
        fieldnames = [
            'name', 'formatted_address', 'place_id', 'phone_number', 'website',
            'rating', 'user_ratings_total', 'business_status', 'place_types',
            'verification_status', 'verification_reason', 'collected_at_stage',
            'last_enriched_stage', 'latitude', 'longitude', 'created_at'
        ]
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for candidate in candidates:
                writer.writerow({
                    'name': candidate.name,
                    'formatted_address': candidate.formatted_address,
                    'place_id': candidate.place_id,
                    'phone_number': candidate.phone_number,
                    'website': candidate.website,
                    'rating': candidate.rating,
                    'user_ratings_total': candidate.user_ratings_total,
                    'business_status': candidate.business_status,
                    'place_types': ';'.join(candidate.place_types),
                    'verification_status': candidate.verification_status,
                    'verification_reason': candidate.verification_reason,
                    'collected_at_stage': candidate.collected_at_stage,
                    'last_enriched_stage': candidate.last_enriched_stage,
                    'latitude': candidate.latitude,
                    'longitude': candidate.longitude,
                    'created_at': candidate.created_at.isoformat()
                })
        
        search_query.processed_results_file = str(csv_file)
        search_query.save()
        
        return str(csv_file)
    
    def generate_summary_report(self, search_query: SearchQuery) -> Dict:
        """Arama sorgusu özet raporu oluştur"""
        
        candidates = search_query.candidates.all()
        
        # İstatistikler
        stats = {
            'total_candidates': candidates.count(),
            'verified_candidates': candidates.filter(verification_status='verified').count(),
            'enriched_candidates': candidates.filter(verification_status='enriched').count(),
            'candidates_with_website': candidates.exclude(website__isnull=True, website='').count(),
            'candidates_with_phone': candidates.exclude(phone_number__isnull=True, phone_number='').count(),
            'candidates_with_enhanced_info': candidates.filter(google_search_enhanced=True).count(),
        }
        
        # API kullanım maliyeti (tahmini)
        api_calls = search_query.api_calls_made
        cost_estimate = 0
        if 'stage1' in api_calls:
            cost_estimate += api_calls['stage1'] * 0.017  # Essentials: $17/1000 requests
        if 'stage2' in api_calls:
            cost_estimate += api_calls['stage2'] * 0.032  # Pro: $32/1000 requests  
        if 'stage3' in api_calls:
            cost_estimate += api_calls['stage3'] * 0.032  # Enterprise: $32/1000 requests
        
        # Özet rapor
        report = {
            'search_info': {
                'query_id': search_query.id,
                'query_text': search_query.query_text,
                'city': search_query.city,
                'sector': search_query.sector,
                'max_stage': search_query.max_stage,
                'status': search_query.status,
                'created_by': search_query.created_by,
                'organization': search_query.organization.name,
                'created_at': search_query.created_at.isoformat(),
                'completed_at': search_query.completed_at.isoformat() if search_query.completed_at else None
            },
            'statistics': stats,
            'api_usage': {
                'calls_made': api_calls,
                'estimated_cost_usd': round(cost_estimate, 4)
            },
            'file_paths': {
                'raw_results': search_query.raw_results_file,
                'processed_results': search_query.processed_results_file
            }
        }
        
        return report
    
    def list_user_searches(self, limit: int = 20) -> List[SearchQuery]:
        """Kullanıcının son aramalarını listele"""
        return SearchQuery.objects.filter(
            created_by=self.user_identifier,
            organization=self.organization
        ).order_by('-created_at')[:limit]
    
    def get_search_by_id(self, search_id: int) -> Optional[SearchQuery]:
        """ID ile arama sorgusunu bul"""
        return SearchQuery.objects.filter(
            id=search_id,
            created_by=self.user_identifier,
            organization=self.organization
        ).first()