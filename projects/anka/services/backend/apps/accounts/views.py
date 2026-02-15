"""
Views for authentication and user management.
"""

import logging
import uuid
from django.conf import settings
from django.utils.text import slugify
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


class GoogleLoginView(APIView):
    """Google-only login endpoint (MVP) - POST /api/auth/google/

    Request:
        {"id_token": "<google_id_token>"}

    Response:
        Same shape as /login/: {access, refresh, user}
    """

    permission_classes = (AllowAny,)

    @extend_schema(
        request=inline_serializer(
            name='GoogleLoginRequest',
            fields={'id_token': serializers.CharField(required=True)},
        ),
        responses={
            200: inline_serializer(
                name='GoogleLoginResponse',
                fields={
                    'access': serializers.CharField(),
                    'refresh': serializers.CharField(),
                    'user': UserDetailSerializer(),
                },
            ),
            401: inline_serializer(
                name='GoogleLoginUnauthorized',
                fields={'error': serializers.CharField()},
            ),
            500: inline_serializer(
                name='GoogleLoginNotConfigured',
                fields={'error': serializers.CharField()},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        google_client_id = getattr(settings, 'GOOGLE_OIDC_CLIENT_ID', None)
        if not google_client_id:
            return Response(
                {'error': 'Google login yapılandırılmamış.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        raw_id_token = request.data.get('id_token')
        if not raw_id_token:
            return Response(
                {'error': 'id_token gereklidir.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from google.oauth2 import id_token as google_id_token
            from google.auth.transport import requests as google_requests

            payload = google_id_token.verify_oauth2_token(
                raw_id_token,
                google_requests.Request(),
                google_client_id,
            )
        except Exception as e:
            logger.warning(f"Google token verification failed: {str(e)}")
            return Response(
                {'error': 'Geçersiz Google oturum anahtarı.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        email = payload.get('email')
        email_verified = payload.get('email_verified')

        if not email or email_verified is False:
            return Response(
                {'error': 'Doğrulanmış email bulunamadı.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        normalized_email = email.strip().lower()
        allowed_google_emails = [
            item.strip().lower()
            for item in getattr(settings, 'ANKA_ALLOWED_GOOGLE_EMAILS', [])
            if str(item).strip()
        ]

        if allowed_google_emails and normalized_email not in allowed_google_emails:
            logger.warning(f"Blocked Google login attempt for unauthorized email: {normalized_email}")
            return Response(
                {'error': 'Bu Google hesabının giriş izni yok.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        first_name = payload.get('given_name') or ''
        last_name = payload.get('family_name') or ''

        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            },
        )

        # Ensure email stays in sync
        if user.email != email:
            user.email = email

        # Fill names if missing
        if not user.first_name and first_name:
            user.first_name = first_name
        if not user.last_name and last_name:
            user.last_name = last_name

        if created or user.has_usable_password():
            # Google-only MVP: make sure password auth isn't accidentally used
            user.set_unusable_password()

        user.save()

        # Ensure profile exists
        UserProfile.objects.get_or_create(user=user)

        # -------------------------------------------------------------
        # Security & Organization Auto-Provisioning
        # -------------------------------------------------------------
        
        # 1. Promote specific admin users
        if normalized_email == 'atalanakin@gmail.com':
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                logger.info(f"User {email} promoted to superuser/staff.")

        # 2. Auto-create personal organization IF user has no memberships
        if not OrganizationMember.objects.filter(user=user).exists():
            with transaction.atomic():
                org_name = f"{first_name} {last_name} Org".strip() or f"{email.split('@')[0]} Org"
                
                # Ensure unique name
                base_name = org_name
                counter = 1
                while Organization.objects.filter(name=org_name).exists():
                    org_name = f"{base_name} {counter}"
                    counter += 1

                # Generate unique slug
                base_slug = slugify(org_name)
                candidate_slug = base_slug
                while Organization.objects.filter(slug=candidate_slug).exists():
                    candidate_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
                
                # Create Org
                org = Organization.objects.create(
                    name=org_name,
                    email=email,
                    slug=candidate_slug,
                    description=f"Personal organization for {email}"
                )

                # Add Member as Owner
                OrganizationMember.objects.create(
                    organization=org,
                    user=user,
                    role='owner',
                    can_create_batches=True,
                    can_download_exports=True,
                    can_manage_disputes=True,
                    can_manage_team=True
                )
                logger.info(f"Auto-created organization '{org_name}' for user {email}")

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserDetailSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class TestLoginView(APIView):
    """Test-only helper: mint JWT for a known user (disabled by default)."""

    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        if not getattr(settings, 'ANKA_ALLOW_TEST_LOGIN', False):
            return Response(status=status.HTTP_404_NOT_FOUND)

        username = request.data.get('username', 'testuser')
        email = request.data.get('email', 'testuser@example.com')

        user, _ = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': 'Test', 'last_name': 'User'},
        )
        UserProfile.objects.get_or_create(user=user)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserDetailSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


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
