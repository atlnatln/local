"""Test için throttle cache'ini temizleyen base test class"""
from rest_framework.test import APITestCase
from django.core.cache import cache


class ThrottleFreeFanıAPITestCase(APITestCase):
    """Throttle cache'ini temizleyen test base class"""
    
    def setUp(self):
        super().setUp()
        # Her test öncesinde cache'i temizle
        cache.clear()
    
    def tearDown(self):
        super().tearDown()
        # Her test sonrasında da cache'i temizle
        cache.clear()
