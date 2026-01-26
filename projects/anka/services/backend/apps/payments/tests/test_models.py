from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.payments.models import PaymentIntent, PaymentTransaction, PaymentWebhook

User = get_user_model()

class PaymentIntentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
    
    def test_create_payment_intent(self):
        intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('99.00'),
            credits=1000,
            conversation_id='test-conv-123',
            status='PENDING'
        )
        self.assertEqual(intent.user, self.user)
        self.assertEqual(intent.amount, Decimal('99.00'))
        self.assertEqual(intent.status, 'PENDING')

    def test_mark_payment_completed(self):
        intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('10.00'),
            credits=100,
            conversation_id='completed-123',
            status='PENDING'
        )
        # Using the constant/lowercase as per model definition
        intent.status = PaymentIntent.COMPLETED
        intent.mark_completed()
        self.assertEqual(intent.status, PaymentIntent.COMPLETED)
        self.assertIsNotNone(intent.completed_at)

class PaymentTransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tuser', password='pwd')
        self.intent = PaymentIntent.objects.create(
            user=self.user, amount=Decimal('50.00'), credits=500, conversation_id='trans-123'
        )

    def test_create_transaction(self):
        transaction = PaymentTransaction.objects.create(
            intent=self.intent,
            iyzico_payment_id='yzc-pay-123',
            iyzico_transaction_id='yzc-trans-123',
            card_last_four='4242',
            status='SUCCESS',
            amount=Decimal('50.00')
        )
        self.assertEqual(transaction.intent, self.intent)
        self.assertEqual(transaction.iyzico_payment_id, 'yzc-pay-123')

class PaymentWebhookModelTest(TestCase):
    def test_create_webhook(self):
        payload = {"test": "data"}
        webhook = PaymentWebhook.objects.create(
            event_type='payment.completed',
            conversation_id='conv-123',
            payload=payload,
            processed=False
        )
        self.assertEqual(webhook.event_type, 'payment.completed')
        self.assertFalse(webhook.processed)
        
        webhook.mark_processed()
        self.assertTrue(webhook.processed)
        self.assertIsNotNone(webhook.processed_at)
