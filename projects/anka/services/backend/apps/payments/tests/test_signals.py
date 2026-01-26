from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from apps.payments.models import PaymentIntent
from apps.ledger.models import CreditPackage, LedgerEntry
from apps.accounts.models import Organization, OrganizationMember

User = get_user_model()

class PaymentSignalsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='siguser', password='pwd')
        # Ensure organization exists
        self.org = Organization.objects.create(name="Sig Org")
        self.member = OrganizationMember.objects.create(organization=self.org, user=self.user, role='owner')

    def test_grant_credits_on_completion(self):
        intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            credits=500,
            conversation_id='sig-123',
            status='PENDING'
        )
        
        # Trigger signal by forcing status update
        intent.status = 'completed'
        # Important: update_fields must be provided as per signal logic
        intent.save(update_fields=['status'])
        
        # Check credit package
        package = CreditPackage.objects.get(organization=self.org)
        self.assertEqual(package.balance, 500)
        
        # Check ledger entry
        self.assertTrue(LedgerEntry.objects.filter(
            reference_id=str(intent.id), 
            transaction_type='purchase'
        ).exists())

    def test_no_credits_if_not_completed(self):
        """Status COMPLETED olmadan kredi verilmemeli."""
        intent = PaymentIntent.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            credits=500,
            conversation_id='sig-fail',
            status='PENDING'
        )
        
        intent.status = 'FAILED'
        intent.save(update_fields=['status'])
        
        # Since we create CreditPackage on demand if not exists, and user has org:
        # Check if balance is still 0 or package not created/not updated if it didn't exist before.
        # But here 'siguser' has 'Sig Org'.
        # Let's see if credits are 0 for this org if we get package.
        
        # If the signal logic creates the package if not found:
        # The logic says: get_or_create credit package...
        # Wait, the log says: if instance.status != 'COMPLETED': return.
        
        # So it should NOT create package if it didn't exist (assuming create defaults work)
        # OR if it exists, it shouldn't add.
        
        # Let's ensure package doesn't exist or has 0 balance.
        package_qs = CreditPackage.objects.filter(organization=self.org)
        if package_qs.exists():
            self.assertEqual(package_qs.first().balance, 0)
        else:
            self.assertTrue(True) # Package not created is also fine
