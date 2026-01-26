from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from decimal import Decimal
from apps.payments.iyzico import IyzicoClient, IyzicoError

# Override settings to ensure we pass the initial check in __init__
@override_settings(
    IYZICO_API_KEY='test_api_key',
    IYZICO_SECRET_KEY='test_secret_key',
    IYZICO_BASE_URL='https://sandbox-api.iyzipay.com'
)
class IyzicoClientTest(TestCase):
    def setUp(self):
        self.client = IyzicoClient()

    @patch('apps.payments.iyzico.iyzipay.CheckoutFormInitialize.create')
    def test_create_payment_success(self, mock_create):
        # Mock success response
        mock_create.return_value = {
            'status': 'success',
            'checkoutFormContent': '<form>content</form>',
            'token': 'test-token-123'
        }
        
        result = self.client.create_payment(
            conversation_id='conv-123',
            amount=Decimal('100.00'),
            user_id=1,
            user_email='test@test.com',
            user_name='Test User'
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['token'], 'test-token-123')

    @patch('apps.payments.iyzico.iyzipay.CheckoutFormInitialize.create')
    def test_create_payment_failure(self, mock_create):
        # Mock failure response
        mock_create.return_value = {
            'status': 'failure',
            'errorMessage': 'Invalid card'
        }

        with self.assertRaises(IyzicoError):
            self.client.create_payment(
                conversation_id='conv-fail',
                amount=Decimal('100.00'),
                user_id=1,
                user_email='test@test.com',
                user_name='Test User'
            )

    @patch('apps.payments.iyzico.iyzipay.CheckoutForm.retrieve')
    def test_confirm_payment_success(self, mock_retrieve):
        mock_retrieve.return_value = {
            'status': 'success',
            'paymentId': 'pay-123',
            'paymentStatus': 'SUCCESS',
            'paidPrice': '100.00',
            'cardLastFour': '4242',
            'cardBin': '123456'
        }
        
        result = self.client.confirm_payment('conv-123', 'token-123')
        self.assertTrue(result['success'])
        self.assertEqual(result['paymentId'], 'pay-123')

    @patch('apps.payments.iyzico.iyzipay.CheckoutForm.retrieve')
    def test_confirm_payment_failure(self, mock_retrieve):
        mock_retrieve.return_value = {
            'status': 'failure',
            'errorMessage': 'Token not found'
        }

        with self.assertRaises(IyzicoError):
            self.client.confirm_payment('conv-fail', 'invalid-token')

    @patch('apps.payments.iyzico.iyzipay.Refund.create')
    def test_refund_payment_success(self, mock_refund):
        mock_refund.return_value = {
            'status': 'success',
            'paymentId': 'pay-123',
            'price': '50.00'
        }

        result = self.client.refund_payment('conv-refund', 'pay-123', Decimal('50.00'))
        self.assertTrue(result['success'])

    @patch('apps.payments.iyzico.iyzipay.Refund.create')
    def test_refund_payment_failure(self, mock_refund):
        mock_refund.return_value = {
            'status': 'failure',
            'errorMessage': 'Refund failed'
        }

        with self.assertRaises(IyzicoError):
            self.client.refund_payment('conv-refund', 'pay-123', Decimal('50.00'))
