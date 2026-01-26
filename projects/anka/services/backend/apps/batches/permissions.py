"""
Custom permissions for batches app.
"""

from rest_framework.permissions import BasePermission

from apps.accounts.models import OrganizationMember


class IsOrganizationMember(BasePermission):
    """Allows access only to members of the batch's organization."""

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        return OrganizationMember.objects.filter(
            organization=obj.organization, user=request.user, is_active=True
        ).exists()
