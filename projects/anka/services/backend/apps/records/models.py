"""
Records app: Firm records with field-level provenance + Google Maps Search Tracking
"""

from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
from apps.batches.models import Batch
from apps.accounts.models import Organization
import json

class Record(models.Model):
    """
    Firm record with field-level provenance tracking
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='records', null=True, blank=True)
    
    # Firm reference
    firm_id = models.CharField(max_length=255, unique=True, db_index=True)
    firm_name = models.CharField(max_length=255)
    
    # Fields (generic - flexibility)
    data = models.JSONField(default=dict)  # All firm data
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'records_record'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['firm_id']),
        ]
    
    def __str__(self):
        return f"Record: {self.firm_name}"


class RecordField(models.Model):
    """
    Field-level provenance: value, verified, source, confidence
    """
    
    SOURCE_CHOICES = (
        ('direct', 'Direct'),  # Provider API
        ('aggregated', 'Aggregated'),  # Multiple sources
        ('inferred', 'Inferred'),  # Derived from other fields
        ('user_provided', 'User Provided'),  # Customer input
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='fields')
    
    # Field definition
    field_name = models.CharField(max_length=255)
    value = models.TextField()
    
    # Provenance
    verified = models.BooleanField(default=False)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default='direct')
    confidence = models.FloatField(default=1.0)  # 0.0 - 1.0
    
    # Source provider
    source_provider = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    observed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'records_record_field'
        unique_together = [['record', 'field_name']]
        ordering = ['-observed_at']
        indexes = [
            models.Index(fields=['record', 'field_name']),
            models.Index(fields=['verified']),
        ]
    
    def __str__(self):
        return f"{self.record.firm_name}.{self.field_name}"


class SearchQuery(models.Model):
    """Gerçekleştirilen arama sorgularını kaydeder"""
    STAGE_CHOICES = [
        ('stage1', 'Stage 1 - ID Collection'),
        ('stage2', 'Stage 2 - Verification'),
        ('stage3', 'Stage 3 - Enrichment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Kullanıcı ve organizasyon bilgileri
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=255)  # username veya system
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Sorgu parametreleri
    query_text = models.CharField(max_length=500)  # "İzmir şehir plancısı" gibi
    city = models.CharField(max_length=100)
    sector = models.CharField(max_length=100)
    location_bias = models.JSONField(null=True, blank=True)  # lat, lng, radius
    
    # Sorgu metadata
    max_stage = models.CharField(max_length=10, choices=STAGE_CHOICES, default='stage1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Sonuçlar
    total_candidates_found = models.IntegerField(default=0)
    api_calls_made = models.JSONField(default=dict)  # {stage1: 5, stage2: 42, stage3: 21}
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=4, default=0)  # USD
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Dosya kayıtları
    raw_results_file = models.CharField(max_length=500, null=True, blank=True)
    processed_results_file = models.CharField(max_length=500, null=True, blank=True)
    
    class Meta:
        db_table = 'search_queries'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.query_text} - {self.organization.name} ({self.status})"
    
    def mark_started(self):
        self.status = 'in_progress'
        self.started_at = timezone.now()
        self.save()
        
    def mark_completed(self, total_found, api_calls):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.total_candidates_found = total_found
        self.api_calls_made = api_calls
        self.save()
        
    def mark_failed(self):
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.save()


class BusinessCandidate(models.Model):
    """Google Places API'den alınan işletme adayları"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('enriched', 'Enriched'),
    ]
    
    # Bağlı olduğu sorgu
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='candidates')
    
    # Google Places API verileri
    place_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=300)
    formatted_address = models.TextField(null=True, blank=True)
    
    # Konum bilgileri
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Google Places metadata
    place_types = models.JSONField(default=list)  # ['point_of_interest', 'establishment']
    business_status = models.CharField(max_length=50, null=True, blank=True)  # OPERATIONAL
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    user_ratings_total = models.IntegerField(null=True, blank=True)
    
    # İletişim bilgileri (Stage 3)
    website = models.URLField(null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    international_phone = models.CharField(max_length=50, null=True, blank=True)
    
    # Doğrulama
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_reason = models.CharField(max_length=100, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # API Stage bilgileri
    collected_at_stage = models.CharField(max_length=10, default='stage1')  # hangi aşamada bulundu
    last_enriched_stage = models.CharField(max_length=10, default='stage1')  # hangi aşamaya kadar zenginleştirildi
    
    # Google Search ile zenginleştirme (ileride eklenecek)
    google_search_enhanced = models.BooleanField(default=False)
    enhanced_website = models.URLField(null=True, blank=True)
    enhanced_phone = models.CharField(max_length=50, null=True, blank=True)
    enhanced_email = models.EmailField(null=True, blank=True)
    social_media_links = models.JSONField(default=dict)  # {'linkedin': 'url', 'facebook': 'url'}
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_candidates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['search_query', 'verification_status']),
            models.Index(fields=['verification_status']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.place_id[:10]}... ({self.verification_status})"
    
    def mark_verified(self, reason):
        self.verification_status = 'verified'
        self.verification_reason = reason
        self.verified_at = timezone.now()
        self.save()
        
    def mark_enriched(self):
        self.verification_status = 'enriched'
        self.save()
    
    @property
    def has_contact_info(self):
        return bool(self.website or self.phone_number or self.enhanced_website or self.enhanced_phone)
    
    @property 
    def complete_contact_info(self):
        return {
            'website': self.enhanced_website or self.website,
            'phone': self.enhanced_phone or self.phone_number,
            'email': self.enhanced_email,
            'social_media': self.social_media_links
        }


class EnrichmentLog(models.Model):
    """Zenginleştirme işlemlerinin logları"""
    ENRICHMENT_TYPE = [
        ('google_search', 'Google Search'),
        ('social_media', 'Social Media Scraping'),
        ('website_analysis', 'Website Analysis'),
        ('phone_verification', 'Phone Number Verification'),
    ]
    
    candidate = models.ForeignKey(BusinessCandidate, on_delete=models.CASCADE, related_name='enrichment_logs')
    enrichment_type = models.CharField(max_length=30, choices=ENRICHMENT_TYPE)
    
    # API/Source bilgileri
    source_api = models.CharField(max_length=100)  # 'Gemini Search Grounding', 'LinkedIn API', etc.
    api_calls_used = models.IntegerField(default=1)
    cost_estimate = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    
    # Sonuçlar
    success = models.BooleanField(default=False)
    data_found = models.JSONField(default=dict)  # Bulunan veriler
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrichment_logs'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.candidate.name} - {self.enrichment_type} ({'✓' if self.success else '✗'})"
