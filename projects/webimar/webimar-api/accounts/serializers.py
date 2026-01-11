from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserSession

class UserProfileSerializer(serializers.ModelSerializer):
    """Kullanıcı profil bilgileri serializer"""
    class Meta:
        model = UserProfile
        fields = ['last_login_ip', 'last_login_time', 'created_at', 'updated_at']
        read_only_fields = ['last_login_ip', 'last_login_time', 'created_at', 'updated_at']

class UserSessionSerializer(serializers.ModelSerializer):
    """Kullanıcı oturum bilgileri serializer"""
    class Meta:
        model = UserSession
        fields = ['session_key', 'ip_address', 'user_agent', 'device_info', 'location', 'login_time', 'last_activity', 'is_active']
        read_only_fields = ['session_key', 'ip_address', 'user_agent', 'device_info', 'location', 'login_time', 'last_activity']

class UserDetailSerializer(serializers.ModelSerializer):
    """Kullanıcı detay bilgileri serializer"""
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_active', 'profile']
        read_only_fields = ['id', 'date_joined', 'is_active']
