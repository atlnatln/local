"""
URLs for payment app.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentIntentViewSet
from .webhooks import iyzico_webhook_handler

router = DefaultRouter()
router.register(r'intents', PaymentIntentViewSet, basename='payment-intent')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/iyzico/', iyzico_webhook_handler, name='iyzico-webhook'),
]
