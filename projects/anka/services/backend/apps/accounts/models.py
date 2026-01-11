"""
Accounts app: User, Organization, and membership management.
"""

from django.db import models
from django.contrib.auth.models import User
import uuid

class Organization(models.Model):
    """Organization (firma/şirket) - müşteri"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Contact
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    country = models.CharField(max_length=100, default='TR')
    city = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_organization'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """Organization membership with roles"""
    
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='org_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    
    # Permissions
    can_create_batches = models.BooleanField(default=False)
    can_download_exports = models.BooleanField(default=False)
    can_manage_disputes = models.BooleanField(default=False)
    can_manage_team = models.BooleanField(default=False)
    
    # Status
    invited_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_organization_member'
        unique_together = [['organization', 'user']]
        ordering = ['-joined_at']
        indexes = [
            models.Index(fields=['organization', 'role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} ({self.role}) @ {self.organization.name}"


class UserProfile(models.Model):
    """Extended user profile"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_url = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='tr', choices=[('tr', 'Türkçe'), ('en', 'English')])
    timezone = models.CharField(max_length=50, default='Europe/Istanbul')
    receive_notifications = models.BooleanField(default=True)
    receive_emails = models.BooleanField(default=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_user_profile'
    
    def __str__(self):
        return f"{self.user.username} Profile"
