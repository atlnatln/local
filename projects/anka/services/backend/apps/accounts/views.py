"""
Views for authentication and user management.
"""

import logging
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, inline_serializer

from .models import Organization, OrganizationMember, UserProfile
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserDetailSerializer,
    ChangePasswordSerializer,
    OrganizationSerializer,
    OrganizationDetailSerializer,
    CreateOrganizationSerializer,
    OrganizationMemberSerializer,
)

logger = logging.getLogger(__name__)


class LoginView(TokenObtainPairView):
    """
    Login endpoint - POST /api/auth/login/
    
    Request:
        {
            "username": "user@example.com",
            "password": "password123"
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "user": {
                "id": 1,
                "username": "user@example.com",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "organizations": [...]
            }
        }
    """
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return Response(
                {'error': 'Kullanıcı adı veya şifre hatalı.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class RegisterView(APIView):
    """
    Register endpoint - POST /api/auth/register/
    
    Request:
        {
            "username": "newuser",
            "email": "user@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
    
    Response:
        {
            "id": 1,
            "username": "newuser",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "profile": {...},
            "organizations": []
        }
    """
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"New user registered: {serializer.data.get('username')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout endpoint - POST /api/auth/logout/
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {"detail": "Başarıyla çıkış yapıldı."}
    """
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=inline_serializer(
            name='LogoutRequest',
            fields={
                'refresh': serializers.CharField(required=True),
            },
        ),
        responses={
            200: inline_serializer(
                name='LogoutResponse',
                fields={'detail': serializers.CharField()},
            ),
            400: inline_serializer(
                name='LogoutError',
                fields={'error': serializers.CharField()},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token gereklidir.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # For JWT, we don't need to do anything on backend
            # Token is invalidated on frontend by deletion
            logger.info(f"User logged out: {request.user.username}")
            return Response(
                {'detail': 'Başarıyla çıkış yapıldı.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return Response(
                {'error': 'Çıkış işlemi başarısız.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class CurrentUserView(APIView):
    """
    Get current user profile - GET /api/auth/me/
    
    Response:
        {
            "id": 1,
            "username": "user@example.com",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "profile": {...},
            "organizations": [...]
        }
    """
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(responses={200: UserDetailSerializer})
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @extend_schema(
        request=inline_serializer(
            name='CurrentUserUpdateRequest',
            fields={
                'first_name': serializers.CharField(required=False, allow_blank=True),
                'last_name': serializers.CharField(required=False, allow_blank=True),
                'email': serializers.EmailField(required=False),
            },
        ),
        responses={200: UserDetailSerializer},
    )
    def patch(self, request):
        """Update current user"""
        user = request.user
        data = request.data
        
        # Only allow certain fields to be updated
        allowed_fields = ['first_name', 'last_name', 'email']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    Change password - POST /api/auth/change-password/
    
    Request:
        {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password2": "newpass123"
        }
    
    Response:
        {"detail": "Şifre başarıyla değiştirildi."}
    """
    permission_classes = (IsAuthenticated,)
    
    @extend_schema(
        request=ChangePasswordSerializer,
        responses={
            200: inline_serializer(
                name='ChangePasswordResponse',
                fields={'detail': serializers.CharField()},
            ),
            400: inline_serializer(
                name='ChangePasswordError',
                fields={'error': serializers.CharField(required=False)},
            ),
        },
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Password changed for user: {request.user.username}")
            return Response(
                {'detail': 'Şifre başarıyla değiştirildi.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization management viewset
    
    Endpoints:
        GET    /api/organizations/           - List all organizations
        POST   /api/organizations/           - Create new organization
        GET    /api/organizations/{id}/      - Retrieve organization
        PATCH  /api/organizations/{id}/      - Update organization
        DELETE /api/organizations/{id}/      - Delete organization
        GET    /api/organizations/{id}/members/ - List members
        POST   /api/organizations/{id}/members/ - Add member
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'id'
    
    def get_queryset(self):
        """Only show organizations user is member of"""
        user = self.request.user
        org_ids = user.org_memberships.values_list('organization_id', flat=True)
        return Organization.objects.filter(id__in=org_ids)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrganizationSerializer
        elif self.action == 'retrieve':
            return OrganizationDetailSerializer
        return OrganizationSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new organization"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info(f"Organization created: {serializer.data.get('name')}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def members(self, request, id=None):
        """Manage organization members"""
        org = self.get_object()
        
        # Check if user is admin/owner
        membership = org.members.filter(user=request.user).first()
        if not membership or membership.role not in ['owner', 'admin']:
            return Response(
                {'error': 'Yetkiniz yok.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if request.method == 'GET':
            members = org.members.select_related('user').filter(is_active=True)
            serializer = OrganizationMemberSerializer(members, many=True)
            return Response(serializer.data)
        
        # POST - Add new member
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'user')
        
        try:
            user = User.objects.get(id=user_id)
            member, created = OrganizationMember.objects.get_or_create(
                organization=org,
                user=user,
                defaults={'role': role}
            )
            
            if not created:
                member.role = role
                member.is_active = True
                member.save()
            
            serializer = OrganizationMemberSerializer(member)
            logger.info(f"User {user.username} added to {org.name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı bulunamadı.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error adding member: {str(e)}")
            return Response(
                {'error': 'Üye eklenemedi.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefreshTokenView(TokenRefreshView):
    """
    Refresh access token - POST /api/auth/refresh/
    
    Request:
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    
    Response:
        {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
        }
    """
    permission_classes = (AllowAny,)
