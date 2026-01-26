"""
Views for ledger app.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.accounts.models import OrganizationMember
from apps.ledger.models import CreditPackage, LedgerEntry
from apps.ledger.serializers import CreditPackageSerializer, LedgerEntrySerializer


class LedgerEntryViewSet(ReadOnlyModelViewSet):
    serializer_class = LedgerEntrySerializer
    permission_classes = [IsAuthenticated]
    queryset = LedgerEntry.objects.all().select_related("organization")
    ordering = ["-created_at"]
    ordering_fields = ["created_at", "transaction_type", "status"]

    def get_queryset(self):
        if not self.request.user or not self.request.user.is_authenticated:
            return LedgerEntry.objects.none()

        org_ids = OrganizationMember.objects.filter(
            user=self.request.user, is_active=True
        ).values_list("organization_id", flat=True)

        return (
            super()
            .get_queryset()
            .filter(organization_id__in=org_ids)
            .select_related("organization")
        )
class CreditBalanceView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreditPackageSerializer

    @extend_schema(responses=CreditPackageSerializer(many=True))
    def get(self, request):
        org_ids = OrganizationMember.objects.filter(
            user=request.user, is_active=True
        ).values_list("organization_id", flat=True)

        queryset = CreditPackage.objects.filter(organization_id__in=org_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
