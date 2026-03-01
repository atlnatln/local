import json
import hmac
import hashlib
from django.test import TestCase, Client
from decimal import Decimal
from django.test.utils import override_settings
from apps.payments.models import PaymentIntent, PaymentTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

class WebhookHandlerTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        self.user = User.objects.create_user(username='webhookuser', password='pwd')
        self.intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('100.00'),
            credits=1000,
            conversation_id='conv-web-123',
            status='PENDING'
        )

    @override_settings(IYZICO_WEBHOOK_SECRET='')
    def test_payment_completed_success(self):
        payload = {
            "eventType": "payment.completed",
            "data": {
                "conversationId": "conv-web-123",
                "paymentId": "pay-999",
                "status": "SUCCESS",
                "transactionId": "trans-999",
                "cardLastFour": "4242",
                "fee": 1.50
            }
        }
        
        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data=payload,
            content_type='application/json',
            secure=True,
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check if intent updated
        self.intent.refresh_from_db()
        self.assertEqual(self.intent.status, 'completed')
        self.assertEqual(self.intent.payment_id, 'pay-999')
        
        # Check if transaction created
        self.assertTrue(PaymentTransaction.objects.filter(iyzico_payment_id='pay-999').exists())

    @override_settings(IYZICO_WEBHOOK_SECRET='test-webhook-secret')
    def test_payment_completed_with_valid_signature(self):
        payload = {
            "eventType": "payment.completed",
            "data": {
                "conversationId": "conv-web-123",
                "paymentId": "pay-1000",
                "status": "SUCCESS",
                "transactionId": "trans-1000",
            }
        }
        body = json.dumps(payload).encode('utf-8')
        signature = hmac.new(
            b'test-webhook-secret',
            body,
            hashlib.sha256,
        ).hexdigest()

        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data=body,
            content_type='application/json',
            HTTP_X_IYZICO_SIGNATURE=signature,
            secure=True,
        )

        self.assertEqual(response.status_code, 200)

    @override_settings(IYZICO_WEBHOOK_SECRET='test-webhook-secret')
    def test_rejects_missing_signature_when_secret_configured(self):
        payload = {
            "eventType": "payment.completed",
            "data": {
                "conversationId": "conv-web-123",
                "paymentId": "pay-1001",
                "status": "SUCCESS",
                "transactionId": "trans-1001",
            }
        }

        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data=payload,
            content_type='application/json',
            secure=True,
        )

        self.assertEqual(response.status_code, 401)

    @override_settings(IYZICO_WEBHOOK_SECRET='test-webhook-secret')
    def test_rejects_invalid_signature(self):
        payload = {
            "eventType": "payment.completed",
            "data": {
                "conversationId": "conv-web-123",
                "paymentId": "pay-1002",
                "status": "SUCCESS",
                "transactionId": "trans-1002",
            }
        }

        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data=payload,
            content_type='application/json',
            HTTP_X_IYZICO_SIGNATURE='invalid-signature',
            secure=True,
        )

        self.assertEqual(response.status_code, 401)

    @override_settings(IYZICO_WEBHOOK_SECRET='')
    def test_payment_failed(self):
        payload = {
            "eventType": "payment.failed",
            "data": {
                "conversationId": "conv-web-123",
                "errorMessage": "Insufficient funds",
                "errorCode": "101"
            }
        }
        
        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data=payload,
            content_type='application/json',
            secure=True,
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.intent.refresh_from_db()
        self.assertEqual(self.intent.status, 'failed')
        self.assertIn("Insufficient funds", self.intent.error_message)

    @override_settings(IYZICO_WEBHOOK_SECRET='')
    def test_invalid_json(self):
        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data="not a json",
            content_type='application/json',
            secure=True,
        )
        # Should handle gracefully with 400
        self.assertEqual(response.status_code, 400)
