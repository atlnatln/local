from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from apps.accounts.models import Organization, OrganizationMember
from apps.batches.models import Batch
from apps.records.models import Record

class RecordAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='password')
        self.org = Organization.objects.create(name='Test Org', slug='test-org')
        OrganizationMember.objects.create(organization=self.org, user=self.user, role='owner')
        
        self.batch = Batch.objects.create(organization=self.org, query_hash='hash123')
        self.record = Record.objects.create(batch=self.batch, firm_id='123', firm_name='Test Firm')
        
        self.client.force_authenticate(user=self.user)

    def test_list_records(self):
        # The URL is registered as router.register(r'', RecordViewSet) under 'api/records/'
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['firm_name'], 'Test Firm')

    def test_filter_records_access(self):
        # User 2 shouldn't see it
        user2 = User.objects.create_user(username='test2', password='password')
        self.client.force_authenticate(user=user2)
        response = self.client.get('/api/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
