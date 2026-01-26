"""
Signals for payment app.
Handles credit granting when payment is completed.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import PaymentIntent
from apps.ledger.models import CreditPackage, LedgerEntry
from apps.accounts.models import Organization, OrganizationMember

logger = logging.getLogger(__name__)


@receiver(post_save, sender=PaymentIntent)
def grant_credits_on_payment_completion(sender, instance, created, update_fields, **kwargs):
    """
    Grant credits to user when payment is completed.
    
    Signal fires after PaymentIntent is saved. Check if status changed to COMPLETED.
    """
    
    # Only process if this is an update and status field was modified
    if created or not update_fields or 'status' not in update_fields:
        return
    
    # Only process completed payments
    if instance.status != PaymentIntent.COMPLETED and instance.status != 'completed':
        return
    
    try:
        # Get organization (user belongs to organization)
        user = instance.user
        member = OrganizationMember.objects.filter(user=user).first()
        
        if member:
            organization = member.organization
        else:
            # Create default organization if none exists
            organization = Organization.objects.create(
                name=f"{user.username}'s Organization",
                # description="Auto-created"
            )
            OrganizationMember.objects.create(
                organization=organization,
                user=user,
                role='owner'
            )
        
        # Get or create credit package for organization
        credit_package, created = CreditPackage.objects.get_or_create(
            organization=organization,
            defaults={'balance': 0, 'total_purchased': 0}
        )
        
        # Calculate new balance
        credits_amount = Decimal(str(instance.credits))
        old_balance = credit_package.balance
        new_balance = old_balance + credits_amount
        
        # Update credit package
        credit_package.balance = new_balance
        credit_package.total_purchased += credits_amount
        credit_package.save()
        
        # Create ledger entry for audit trail
        LedgerEntry.objects.create(
            organization=organization,
            transaction_type='purchase',
            amount=credits_amount,
            status='completed',
            reference_type='payment',
            reference_id=str(instance.id),
            description=f"Credit purchase - {instance.credits} credits @ ₺{instance.amount}",
            balance_before=old_balance,
            balance_after=new_balance,
            metadata={
                'payment_id': str(instance.id),
                'payment_intent_id': str(instance.id),
                'amount_paid': str(instance.amount),
                'credits_granted': instance.credits,
            }
        )
        
        logger.info(
            f"Credits granted: user={user.id}, "
            f"credits={instance.credits}, balance={new_balance}"
        )
    
    except Exception as e:
        logger.exception(f"Error granting credits for payment {instance.id}: {str(e)}")


@receiver(post_save, sender=PaymentIntent)
def revoke_credits_on_payment_failure(sender, instance, created, update_fields, **kwargs):
    """
    Revoke credits if payment is marked as FAILED after being COMPLETED.
    (Safety mechanism for dispute cases)
    """
    
    if created or not update_fields or 'status' not in update_fields:
        return
    
    # Only process failed payments that were previously completed
    if instance.status != 'FAILED':
        return
    
    try:
        # Check if there's already a purchase ledger entry
        existing_entry = LedgerEntry.objects.filter(
            reference_type='payment',
            reference_id=str(instance.id),
            transaction_type='purchase'
        ).first()
        
        if not existing_entry:
            # No credits were granted, nothing to revoke
            return
        
        # Get organization
        user = instance.user
        organization = Organization.objects.filter(users=user).first()
        if not organization:
            return
        
        # Get credit package
        credit_package = CreditPackage.objects.filter(organization=organization).first()
        if not credit_package:
            return
        
        # Revoke credits
        credits_to_revoke = Decimal(str(instance.credits))
        old_balance = credit_package.balance
        new_balance = max(old_balance - credits_to_revoke, Decimal('0'))  # Don't go negative
        
        credit_package.balance = new_balance
        credit_package.save()
        
        # Create refund ledger entry
        LedgerEntry.objects.create(
            organization=organization,
            transaction_type='refund',
            amount=credits_to_revoke,
            status='completed',
            reference_type='payment',
            reference_id=str(instance.id),
            description=f"Credit refund - {instance.credits} credits (payment failed)",
            balance_before=old_balance,
            balance_after=new_balance,
        )
        
        logger.info(
            f"Credits revoked: user={user.id}, "
            f"credits={instance.credits}, balance={new_balance}"
        )
    
    except Exception as e:
        logger.exception(f"Error revoking credits for payment {instance.id}: {str(e)}")
