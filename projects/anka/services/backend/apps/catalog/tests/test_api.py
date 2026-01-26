from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apps.catalog.models import City, Sector

class CatalogAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='password')
        self.client.force_authenticate(user=self.user)
        
        self.city = City.objects.create(name='Istanbul', code='34')
        self.sector = Sector.objects.create(name='Teknoloji', code='TECH')

    def test_list_cities(self):
        response = self.client.get('/api/catalog/cities/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Istanbul')

    def test_list_sectors(self):
        response = self.client.get('/api/catalog/sectors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Teknoloji')
