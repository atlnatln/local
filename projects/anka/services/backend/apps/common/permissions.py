"""
Custom permission classes for the API.
"""

from rest_framework.permissions import BasePermission


class IsOrganizationMember(BasePermission):
    """
    Allows access only to users who are members of the organization.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the organization"""
        try:
            # For Organization objects
            if hasattr(obj, 'members'):
                return obj.members.filter(user=request.user, is_active=True).exists()
            
            # For objects with organization FK (Batch, Dispute, etc.)
            if hasattr(obj, 'organization'):
                return obj.organization.members.filter(user=request.user, is_active=True).exists()
            
            # For User objects
            if hasattr(obj, 'user') and obj.user == request.user:
                return True
            
            return False
        except Exception:
            return False


class IsOrganizationOwnerOrAdmin(BasePermission):
    """
    Allows access only to organization owner or admin.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin of the organization"""
        try:
            org = obj if hasattr(obj, 'members') else getattr(obj, 'organization', None)
            if not org:
                return False
            
            membership = org.members.filter(
                user=request.user,
                is_active=True,
                role__in=['owner', 'admin']
            ).exists()
            
            return membership
        except Exception:
            return False


class IsBatchCreator(BasePermission):
    """
    Allows access only to users who created the batch or are organization admins.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user created the batch or is org admin"""
        if not hasattr(obj, 'organization'):
            return False
        
        org = obj.organization
        
        # Check if user is owner/admin of organization
        is_admin = org.members.filter(
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists()
        
        # Check if user can create batches
        if is_admin:
            return True
        
        member = org.members.filter(user=request.user, is_active=True).first()
        if member and member.can_create_batches:
            return True
        
        return False


class CanDownloadExports(BasePermission):
    """
    Allows downloading exports only to authorized users.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can download exports"""
        if not hasattr(obj, 'organization'):
            return False
        
        org = obj.organization
        member = org.members.filter(user=request.user, is_active=True).first()
        
        return member and member.can_download_exports


class CanManageDisputes(BasePermission):
    """
    Allows managing disputes only to authorized users.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can manage disputes"""
        if not hasattr(obj, 'organization'):
            return False
        
        org = obj.organization
        member = org.members.filter(user=request.user, is_active=True).first()
        
        return member and member.can_manage_disputes
