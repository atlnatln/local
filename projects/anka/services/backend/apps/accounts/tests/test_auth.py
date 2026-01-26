"""
Tests for authentication and account management.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Organization, OrganizationMember, UserProfile


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def user_with_profile(user):
    """Create a test user with profile"""
    UserProfile.objects.create(user=user)
    return user


@pytest.fixture
def organization(db, user_with_profile):
    """Create a test organization"""
    org = Organization.objects.create(
        name='Test Organization',
        slug='test-org',
        email='org@example.com',
        country='TR',
    )
    OrganizationMember.objects.create(
        organization=org,
        user=user_with_profile,
        role='owner',
        can_create_batches=True,
        can_download_exports=True,
        can_manage_disputes=True,
        can_manage_team=True,
    )
    return org


class TestLogin:
    """Test login functionality"""
    
    def test_login_success(self, client, user_with_profile):
        """Test successful login"""
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
        assert response.data['user']['username'] == 'testuser'
        assert response.data['user']['email'] == 'test@example.com'
    
    def test_login_invalid_credentials(self, client, user_with_profile):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post('/api/auth/login/', {
            'username': 'nonexistent',
            'password': 'TestPass123!'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_password(self, client, user_with_profile):
        """Test login without password"""
        response = client.post('/api/auth/login/', {
            'username': 'testuser',
        })
        
        # Missing password returns 401 (invalid credentials) not 400
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]


class TestRegister:
    """Test user registration"""
    
    def test_register_success(self, client):
        """Test successful registration"""
        response = client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@example.com'
        assert response.data['first_name'] == 'John'
        
        # Verify user was created in DB
        user = User.objects.get(username='newuser')
        assert user.email == 'newuser@example.com'
        
        # Verify profile was created
        assert hasattr(user, 'profile')
    
    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
    
    def test_register_duplicate_email(self, client, user_with_profile):
        """Test registration with duplicate email"""
        response = client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'test@example.com',  # Existing email
            'password': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data
    
    def test_register_weak_password(self, client):
        """Test registration with weak password"""
        response = client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123',  # Too weak
            'password2': '123',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCurrentUser:
    """Test current user endpoint"""
    
    def test_get_current_user(self, client, user_with_profile):
        """Test getting current user profile"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.get('/api/auth/me/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['email'] == 'test@example.com'
        assert 'profile' in response.data
    
    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user without authentication"""
        response = client.get('/api/auth/me/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_current_user(self, client, user_with_profile):
        """Test updating current user"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.patch('/api/auth/me/', {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['first_name'] == 'Jane'
        assert response.data['last_name'] == 'Smith'
        assert response.data['email'] == 'jane@example.com'
        
        # Verify changes in DB
        user = User.objects.get(id=user_with_profile.id)
        assert user.first_name == 'Jane'


class TestChangePassword:
    """Test password change"""
    
    def test_change_password_success(self, client, user_with_profile):
        """Test successful password change"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.post('/api/auth/change-password/', {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password was changed
        user = User.objects.get(id=user_with_profile.id)
        assert user.check_password('NewPass123!')
    
    def test_change_password_wrong_old(self, client, user_with_profile):
        """Test password change with wrong old password"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.post('/api/auth/change-password/', {
            'old_password': 'WrongPassword',
            'new_password': 'NewPass123!',
            'new_password2': 'NewPass123!',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'old_password' in response.data
    
    def test_change_password_mismatch(self, client, user_with_profile):
        """Test password change with mismatched new passwords"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.post('/api/auth/change-password/', {
            'old_password': 'TestPass123!',
            'new_password': 'NewPass123!',
            'new_password2': 'DifferentPass123!',
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRefreshToken:
    """Test token refresh"""
    
    def test_refresh_token_success(self, client, user_with_profile):
        """Test successful token refresh"""
        # First login to get tokens
        login_response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        refresh_token = login_response.data['refresh']
        
        # Now refresh
        response = client.post('/api/auth/refresh/', {
            'refresh': refresh_token
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_refresh_token_invalid(self, client):
        """Test refresh with invalid token"""
        response = client.post('/api/auth/refresh/', {
            'refresh': 'invalid_token'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Test logout functionality"""
    
    def test_logout_success(self, client, user_with_profile):
        """Test successful logout"""
        client.force_authenticate(user=user_with_profile)
        
        login_response = client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'TestPass123!'
        })
        
        refresh_token = login_response.data['refresh']
        
        response = client.post('/api/auth/logout/', {
            'refresh': refresh_token
        })
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_logout_without_refresh_token(self, client, user_with_profile):
        """Test logout without refresh token"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.post('/api/auth/logout/', {})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestOrganizations:
    """Test organization management"""
    
    def test_create_organization(self, client, user_with_profile):
        """Test creating a new organization"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.post('/api/auth/organizations/', {
            'name': 'New Company',
            'slug': 'new-company',
            'email': 'company@example.com',
            'country': 'TR',
            'city': 'Istanbul',
        })
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Company'
        assert response.data['slug'] == 'new-company'
        
        # Verify organization was created
        org = Organization.objects.get(slug='new-company')
        
        # Verify creator is owner
        member = org.members.get(user=user_with_profile)
        assert member.role == 'owner'
        assert member.can_create_batches
        assert member.can_manage_team
    
    def test_list_organizations(self, client, user_with_profile, organization):
        """Test listing user's organizations"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.get('/api/auth/organizations/')
        
        assert response.status_code == status.HTTP_200_OK
        # Response is paginated dict
        if isinstance(response.data, dict) and 'results' in response.data:
            results = response.data['results']
            assert len(results) >= 1
            assert any(org['id'] == str(organization.id) for org in results)
        else:
            # Non-paginated response (list)
            assert len(response.data) >= 1
            assert any(org['id'] == str(organization.id) for org in response.data)
    
    def test_get_organization(self, client, user_with_profile, organization):
        """Test getting organization details"""
        client.force_authenticate(user=user_with_profile)
        
        response = client.get(f'/api/auth/organizations/{organization.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Organization'
        assert 'members' in response.data
    
    def test_add_organization_member(self, client, user_with_profile, organization):
        """Test adding a member to organization"""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        UserProfile.objects.create(user=other_user)
        
        client.force_authenticate(user=user_with_profile)
        
        response = client.post(
            f'/api/auth/organizations/{organization.id}/members/',
            {
                'user_id': other_user.id,
                'role': 'admin',
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['role'] == 'admin'
        
        # Verify member was added
        member = organization.members.get(user=other_user)
        assert member.role == 'admin'
    
    def test_organization_permissions(self, client):
        """Test that non-members can't access organization"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='TestPass123!'
        )
        UserProfile.objects.create(user=other_user)
        
        org = Organization.objects.create(
            name='Private Org',
            slug='private-org',
            email='private@example.com',
        )
        
        client.force_authenticate(user=other_user)
        
        response = client.get(f'/api/auth/organizations/{org.id}/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
