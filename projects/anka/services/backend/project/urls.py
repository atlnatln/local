"""
Project-wide URL configuration for Anka Backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from apps.batches.views import BatchViewSet
from apps.credits.views import CreditPurchaseView
from apps.disputes.views import DisputeViewSet
from apps.exports.views import ExportViewSet
from apps.ledger.views import CreditBalanceView, LedgerEntryViewSet

def health_check(request):
    return JsonResponse({'status': 'ok'})


router = DefaultRouter()
router.register(r'batches', BatchViewSet, basename='batches')
router.register(r'exports', ExportViewSet, basename='exports')
router.register(r'disputes', DisputeViewSet, basename='disputes')
router.register(r'ledger/entries', LedgerEntryViewSet, basename='ledger-entries')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Schema
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('api/health/', health_check),

    # Authentication & Accounts
    path('api/auth/', include('apps.accounts.urls')),

    # Credits
    path('api/credits/balance/', CreditBalanceView.as_view(), name='credits-balance'),
    path('api/credits/purchase/', CreditPurchaseView.as_view(), name='credits-purchase'),
    
    # Payments
    path('api/payments/', include('apps.payments.urls')),

    # Catalog
    path('api/catalog/', include('apps.catalog.urls')),

    # Records
    path('api/records/', include('apps.records.urls')),

    # API routes
    path('api/', include(router.urls)),
]
