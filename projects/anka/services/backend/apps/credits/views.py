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
    """Get current credit balance for authenticated user.

    Returns a JSON **array** of CreditPackage objects (one per org membership).
    Frontend sums `balance` across all entries to display total.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        from apps.accounts.models import OrganizationMember

        # Find all organisations the user belongs to (via OrganizationMember)
        org_ids = (
            OrganizationMember.objects
            .filter(user=user, is_active=True)
            .values_list('organization_id', flat=True)
        )

        results = []
        for org in Organization.objects.filter(id__in=org_ids):
            credit_package, _ = CreditPackage.objects.get_or_create(
                organization=org,
                defaults={'balance': 0},
            )
            results.append({
                'id': str(credit_package.id),
                'organization': str(org.id),
                'organization_name': org.name,
                'balance': str(credit_package.balance),
                'total_purchased': str(credit_package.total_purchased),
                'total_spent': str(credit_package.total_spent),
                'total_refunded': str(credit_package.total_refunded),
                'is_active': credit_package.is_active,
            })

        return Response(results)