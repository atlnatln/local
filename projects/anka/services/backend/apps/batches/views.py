"""
ViewSets for batches app.
"""

from decimal import Decimal
import logging

from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import OrganizationMember
from apps.batches.models import Batch, BatchItem
from apps.batches.permissions import IsOrganizationMember
from apps.batches.serializers import BatchItemSerializer, BatchListSerializer, BatchSerializer
from apps.batches.tasks import process_batch_task
from apps.ledger.models import CreditPackage, LedgerEntry

logger = logging.getLogger(__name__)


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated, IsOrganizationMember]
    queryset = Batch.objects.all().select_related("organization")
    search_fields = ["city", "sector", "query_hash", "status"]
    ordering_fields = ["created_at", "status", "city", "sector"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Use lightweight serializer for list action (no nested items)."""
        if self.action == "list":
            return BatchListSerializer
        return BatchSerializer

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return Batch.objects.none()

        org_ids = OrganizationMember.objects.filter(
            user=self.request.user, is_active=True
        ).values_list("organization_id", flat=True)

        return (
            super()
            .get_queryset()
            .filter(organization_id__in=org_ids)
            .select_related("organization")
        )

    def perform_create(self, serializer):
        organization = serializer.validated_data.get("organization")
        is_member = OrganizationMember.objects.filter(
            organization=organization, user=self.request.user, is_active=True
        ).exists()
        if not is_member:
            raise PermissionDenied("Organization erişimi yok.")

        record_count_estimate = serializer.validated_data.get("record_count_estimate") or 0
        estimated_cost = Decimal(str(record_count_estimate))

        with transaction.atomic():
            credit_package, _ = CreditPackage.objects.select_for_update().get_or_create(
                organization=organization
            )
            balance_before = Decimal(credit_package.balance)
            if estimated_cost > 0 and balance_before < estimated_cost:
                raise ValidationError({"detail": "Yetersiz kredi bakiyesi."})

            batch = serializer.save(
                created_by=self.request.user.username,
                estimated_cost=estimated_cost,
            )

            if estimated_cost > 0:
                credit_package.balance = F("balance") - estimated_cost
                credit_package.total_spent = F("total_spent") + estimated_cost
                credit_package.save(update_fields=["balance", "total_spent", "updated_at"])
                credit_package.refresh_from_db()

                # Ledger entry oluştur (idempotent: get_or_create ile, constraint violation handling)
                try:
                    ledger_entry, created = LedgerEntry.objects.get_or_create(
                        reference_type="batch",
                        reference_id=str(batch.id),
                        defaults={
                            "organization": organization,
                            "transaction_type": "spent",
                            "amount": estimated_cost,
                            "status": "completed",
                            "description": "Batch oluşturma ücreti",
                            "balance_before": balance_before,
                            "balance_after": Decimal(credit_package.balance),
                            "metadata": {"batch_id": str(batch.id)},
                        }
                    )
                    if not created:
                        # Ledger kaydı zaten var (idempotent call)
                        logger.info(f"Ledger entry already exists for batch {batch.id}, skipping duplicate")
                except IntegrityError as e:
                    # Eğer yine de constraint violation çıkarsa, loglayıp ValidationError döndür
                    logger.error(f"IntegrityError while creating ledger for batch {batch.id}: {str(e)}")
                    raise ValidationError(
                        {"detail": "Ledger kaydı oluşturulurken constraint violation (bu batch zaten işlenmiş olabilir)."}
                    )
        
        # Trigger processing task — wrapped so Redis hiccups don't kill the 201
        def _dispatch():
            try:
                process_batch_task.apply_async(
                    args=[batch.id],
                    ignore_result=True,
                )
            except Exception as dispatch_err:  # noqa: BLE001
                logger.error(
                    "Batch %s created but task dispatch failed (Redis?): %s",
                    batch.id,
                    dispatch_err,
                )

        transaction.on_commit(_dispatch)

    @action(detail=True, methods=["get"], url_path="items")
    def items(self, request, pk=None):
        batch = self.get_object()
        queryset = BatchItem.objects.filter(batch=batch).order_by("created_at")
        serializer = BatchItemSerializer(queryset, many=True)
        return Response(serializer.data)
