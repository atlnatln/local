"""
Serializers for credits app.
"""

from rest_framework import serializers

from apps.accounts.models import Organization, OrganizationMember


class CreditPurchaseSerializer(serializers.Serializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=1)

    def validate_organization(self, organization):
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return organization

        is_member = OrganizationMember.objects.filter(
            organization=organization, user=request.user, is_active=True
        ).exists()
        if not is_member:
            raise serializers.ValidationError("Organization erişimi yok.")

        return organization


class CreditPurchaseResponseSerializer(serializers.Serializer):
    organization = serializers.UUIDField()
    balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_purchased = serializers.DecimalField(max_digits=12, decimal_places=2)
