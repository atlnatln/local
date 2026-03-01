"""
Serializers for authentication and user management.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from .models import Organization, OrganizationMember, UserProfile


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id',)


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user information with profile"""
    
    profile = serializers.SerializerMethodField()
    organizations = serializers.SerializerMethodField()
    has_usable_password = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile', 'organizations', 'date_joined', 'has_usable_password')
        read_only_fields = ('id', 'date_joined')
    
    def get_profile(self, obj) -> dict | None:
        if hasattr(obj, 'profile'):
            return UserProfileSerializer(obj.profile).data
        return None

    def get_has_usable_password(self, obj) -> bool:
        """True if user has a usable (non-Google) password."""
        return obj.has_usable_password()
    
    def get_organizations(self, obj) -> list[dict]:
        """Get organizations this user is member of"""
        memberships = obj.org_memberships.select_related('organization').all()
        return [
            {
                'id': m.organization.id,
                'name': m.organization.name,
                'role': m.role,
                'slug': m.organization.slug,
            }
            for m in memberships
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile extended data"""
    
    class Meta:
        model = UserProfile
        fields = ('id', 'avatar_url', 'phone', 'language', 'timezone', 'receive_notifications', 'receive_emails')
        read_only_fields = ('id',)


class LoginSerializer(TokenObtainPairSerializer):
    """Custom login serializer to return user data with token"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user information to response
        user = self.user
        data['user'] = UserDetailSerializer(user).data
        data['access'] = str(data['access'])
        data['refresh'] = str(data['refresh'])
        
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Şifreler eşleşmiyor.'
            })
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({
                'email': 'Bu email zaten kayıtlı.'
            })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        return user
    
    def to_representation(self, instance):
        return UserDetailSerializer(instance).data


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'Yeni şifreler eşleşmiyor.'
            })
        
        user = self.context['request'].user
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': 'Eski şifre yanlış.'
            })
        
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization basic serializer"""
    
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'email', 'description', 'country', 'city', 'is_active', 'member_count', 'created_at')
        read_only_fields = ('id', 'created_at')

    @extend_schema_field(OpenApiTypes.INT)
    def get_member_count(self, obj) -> int:
        return obj.members.filter(is_active=True).count()


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Organization member with user details"""

    user = UserBasicSerializer(read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ('id', 'user', 'role', 'can_create_batches', 'can_download_exports', 'can_manage_disputes', 'can_manage_team', 'joined_at')
        read_only_fields = ('id', 'joined_at')


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Organization with members and details"""
    
    members = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ('id', 'name', 'slug', 'description', 'email', 'phone', 'website', 'country', 'city', 'is_active', 'verified_at', 'members', 'metadata', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    @extend_schema_field(OrganizationMemberSerializer(many=True))
    def get_members(self, obj):
        members = obj.members.select_related('user').filter(is_active=True)
        return OrganizationMemberSerializer(members, many=True).data


class CreateOrganizationSerializer(serializers.ModelSerializer):
    """Create organization serializer"""
    
    class Meta:
        model = Organization
        fields = ('name', 'slug', 'description', 'email', 'phone', 'website', 'country', 'city')
    
    @transaction.atomic
    def create(self, validated_data):
        org = Organization.objects.create(**validated_data)
        
        # Add current user as owner
        user = self.context['request'].user
        OrganizationMember.objects.create(
            organization=org,
            user=user,
            role='owner',
            can_create_batches=True,
            can_download_exports=True,
            can_manage_disputes=True,
            can_manage_team=True,
        )
        
        return org
    
    def to_representation(self, instance):
        return OrganizationSerializer(instance).data
