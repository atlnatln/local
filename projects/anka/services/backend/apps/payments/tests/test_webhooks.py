import json
from django.test import TestCase, Client
from decimal import Decimal
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
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check if intent updated
        self.intent.refresh_from_db()
        self.assertEqual(self.intent.status, 'completed')
        self.assertEqual(self.intent.payment_id, 'pay-999')
        
        # Check if transaction created
        self.assertTrue(PaymentTransaction.objects.filter(iyzico_payment_id='pay-999').exists())

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
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        self.intent.refresh_from_db()
        self.assertEqual(self.intent.status, 'failed')
        self.assertIn("Insufficient funds", self.intent.error_message)

    def test_invalid_json(self):
        response = self.client.post(
            '/api/payments/webhooks/iyzico/',
            data="not a json",
            content_type='application/json'
        )
        # Should handle gracefully with 400
        self.assertEqual(response.status_code, 400)
