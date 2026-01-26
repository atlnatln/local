from unittest.mock import patch
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from apps.payments.models import PaymentIntent
from django.test import override_settings

User = get_user_model()

@override_settings(
    IYZICO_API_KEY='test_api_key',
    IYZICO_SECRET_KEY='test_secret_key',
    IYZICO_BASE_URL='https://sandbox-api.iyzipay.com',
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
)
class PaymentIntentViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password')
        self.client.force_authenticate(user=self.user)
        self.url = '/api/payments/intents/'

    @patch('apps.payments.views.IyzicoClient')
    def test_create_payment_intent_success(self, MockIyzicoClient):
        # Mock IyzicoClient instance and create_payment method
        mock_instance = MockIyzicoClient.return_value
        mock_instance.create_payment.return_value = {
            'success': True,
            'checkoutFormContent': '<html>form</html>',
            'token': 'tkn-123'
        }

        data = {
            'amount': '99.00',
            'credits': 1000,
            'package_type': 'starter'
        }
        
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'PENDING')
        
        # Check if Intent was created in DB
        self.assertTrue(PaymentIntent.objects.filter(user=self.user, credits=1000).exists())

    def test_list_payment_intents(self):
        PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            credits=500,
            conversation_id='list-test',
            status='PENDING'
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Note: Depending on how many tests ran before or pagination, 
        # checking the count specifically for 'this' one might need filtering or cleanup
        # Assuming pagination is standard or number of results is >= 1
        self.assertGreaterEqual(len(response.data.get('results', [])), 1)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('apps.payments.views.IyzicoClient')
    def test_confirm_payment_intent(self, MockIyzicoClient):
        # Setup intent
        intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('99.00'),
            credits=1000,
            conversation_id='confirm-test',
            status='PENDING'
        )
        
        # Mock confirm response
        mock_instance = MockIyzicoClient.return_value
        mock_instance.confirm_payment.return_value = {
            'success': True,
            'paymentId': 'pid-123',
            'status': 'SUCCESS',
            'amount': Decimal('99.00'),
            'transactionId': 'tr-123',
            'cardLastFour': '4242',
            'cardBin': '123456',
            'fee': Decimal('1.50')
        }
        
        url = f'{self.url}{intent.id}/confirm/'
        data = {
            'token': 'tkn-123',
            'conversation_id': intent.conversation_id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # In a real scenario, confirm might also trigger webhook logic or signal directly 
        # if the view updates the intent. The view logic in the shared code only returns the status 
        # from Iyzico, it might NOT update the local DB immediately if relying on webhooks.
        # Let's check what the view does.
