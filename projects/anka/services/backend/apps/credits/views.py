"""
Views for credits app.
"""

from decimal import Decimal

from drf_spectacular.utils import extend_schema
from django.db import transaction
from django.db.models import F
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.ledger.models import CreditPackage, LedgerEntry
from apps.accounts.models import Organization
from apps.credits.serializers import CreditPurchaseResponseSerializer, CreditPurchaseSerializer


class CreditPurchaseView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreditPurchaseSerializer

    @extend_schema(
        request=CreditPurchaseSerializer,
        responses=CreditPurchaseResponseSerializer,
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = serializer.validated_data["organization"]
        amount = serializer.validated_data["amount"]

        with transaction.atomic():
            credit_package, _ = CreditPackage.objects.select_for_update().get_or_create(
                organization=organization
            )

            balance_before = Decimal(credit_package.balance)

            credit_package.balance = F("balance") + amount
            credit_package.total_purchased = F("total_purchased") + amount
            credit_package.save(update_fields=["balance", "total_purchased", "updated_at"])

            credit_package.refresh_from_db()
            balance_after = Decimal(credit_package.balance)

            LedgerEntry.objects.create(
                organization=organization,
                transaction_type="purchase",
                amount=amount,
                status="completed",
                reference_type="payment",
                reference_id=f"manual_{organization.id}",
                description="Manual credit purchase",
                balance_before=balance_before,
                balance_after=balance_after,
                metadata={"source": "manual"},
            )
        response_serializer = CreditPurchaseResponseSerializer(
            {
                "organization": organization.id,
                "balance": credit_package.balance,
                "total_purchased": credit_package.total_purchased,
            }
        )
        return Response(response_serializer.data)

class CreditBalanceView(GenericAPIView):
    """Get current credit balance for authenticated user."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get credit balance for current user's organization.
        
        Response:
        {
            "organization_id": "uuid",
            "organization_name": "User's Organization",
            "balance": 1000,
            "total_purchased": 5000,
            "total_spent": 4000,
            "total_refunded": 0,
            "is_active": true
        }
        """
        user = request.user
        
        # Get user's organization
        organization = user.organizations.first()
        if not organization:
            # Create default organization if not exists
            organization = Organization.objects.create(
                name=f"{user.username}'s Organization",
                owner=user,
            )
            organization.users.add(user)
        
        # Get credit package
        credit_package, _ = CreditPackage.objects.get_or_create(
            organization=organization,
            defaults={'balance': 0}
        )
        
        return Response({
            'organization_id': str(organization.id),
            'organization_name': organization.name,
            'balance': credit_package.balance,
            'total_purchased': credit_package.total_purchased,
            'total_spent': credit_package.total_spent,
            'total_refunded': credit_package.total_refunded,
            'is_active': credit_package.is_active,
        })