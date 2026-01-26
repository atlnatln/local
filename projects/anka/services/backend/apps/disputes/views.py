"""
ViewSets for disputes app.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import OrganizationMember
from apps.disputes.models import Dispute, DisputeItem
from apps.disputes.rule_engine import DecisionEngine
from apps.disputes.serializers import DisputeCreateSerializer, DisputeSerializer
from apps.ledger.models import CreditPackage, LedgerEntry


class DisputeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Dispute.objects.all().select_related("organization", "batch")
    ordering = ["-created_at"]
    ordering_fields = ["created_at", "status", "decision"]

    def get_serializer_class(self):
        if self.action in {"create"}:
            return DisputeCreateSerializer
        return DisputeSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Dispute.objects.none()

        org_ids = OrganizationMember.objects.filter(
            user=self.request.user, is_active=True
        ).values_list("organization_id", flat=True)

        return super().get_queryset().filter(organization_id__in=org_ids)

    def perform_create(self, serializer):
        organization = serializer.validated_data.get("organization")
        batch = serializer.validated_data.get("batch")
        items = serializer.validated_data.pop("items", [])

        is_member = OrganizationMember.objects.filter(
            organization=organization, user=self.request.user, is_active=True
        ).exists()
        if not is_member or batch.organization_id != organization.id:
            raise PermissionDenied("Organization erişimi yok.")

        decision, reason_code = DecisionEngine.evaluate(
            serializer.validated_data.get("evidence_data") or {}
        )

        refund_amount = Decimal(len(items))

        with transaction.atomic():
            dispute = serializer.save(
                status="resolved",
                decision=decision,
                decision_reason_code=reason_code,
                refund_amount=refund_amount if decision == "accept" else Decimal("0"),
                resolved_at=timezone.now(),
            )

            for item in items:
                DisputeItem.objects.create(dispute=dispute, **item)

            if decision == "accept" and refund_amount > 0:
                credit_package, _ = CreditPackage.objects.select_for_update().get_or_create(
                    organization=organization
                )
                balance_before = Decimal(credit_package.balance)
                credit_package.balance = F("balance") + refund_amount
                credit_package.total_refunded = F("total_refunded") + refund_amount
                credit_package.save(update_fields=["balance", "total_refunded", "updated_at"])

                credit_package.refresh_from_db()
                balance_after = Decimal(credit_package.balance)

                LedgerEntry.objects.create(
                    organization=organization,
                    transaction_type="refund",
                    amount=refund_amount,
                    status="completed",
                    reference_type="dispute",
                    reference_id=str(dispute.id),
                    description="Dispute refund",
                    balance_before=balance_before,
                    balance_after=balance_after,
                    metadata={"rule": reason_code},
                )
