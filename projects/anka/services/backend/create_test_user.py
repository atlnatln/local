import os
import sys
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings.dev')
django.setup()

User = get_user_model()
username = 'testuser'
email = 'test@example.com'

# Secure password generation
import secrets
import string
def generate_strong_password(length=32):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))

password = os.environ.get('TEST_USER_PASSWORD')
if not password:
    password = generate_strong_password()
    # Write generated password to stderr only (never stdout)
    print(f"INFO: Generated random secure password for {username}", file=sys.stderr)
    print(f"TEST_USER_PASSWORD={password}", file=sys.stderr)
else:
    print(f"INFO: Using provided TEST_USER_PASSWORD for {username}", file=sys.stderr)

if not User.objects.filter(username=username).exists():
    user = User.objects.create_user(username=username, email=email, password=password)
    print(f"User {username} created.")
else:
    print(f"User {username} already exists.")
    user = User.objects.get(username=username)

# Create Organization if needed for other tests
try:
    from apps.accounts.models import Organization, OrganizationMember
    from django.utils.text import slugify
    
    org_name = "Test Org"
    if not Organization.objects.filter(name=org_name).exists():
        org = Organization.objects.create(
            name=org_name, 
            slug=slugify(org_name), 
            email='testorg@example.com'
        )
        print(f"Organization {org_name} created.")
        
        OrganizationMember.objects.create(
            organization=org, 
            user=user, 
            role='owner', 
            is_active=True
        )
        print(f"Membership for {username} created.")
    else:
        # Ensure membership exists if org exists
        org = Organization.objects.get(name=org_name)
        if not OrganizationMember.objects.filter(organization=org, user=user).exists():
            OrganizationMember.objects.create(
                organization=org, 
                user=user, 
                role='owner', 
                is_active=True
            )
            print(f"Added membership for {username} to {org_name}.")
        else:
            print(f"Membership for {username} already exists.")

except ImportError:
    pass

# Seed Catalog
try:
    from apps.catalog.models import City, Sector
    
    cities = ['Istanbul', 'Ankara', 'Izmir']
    for c_name in cities:
        City.objects.get_or_create(
            name=c_name, 
            defaults={'code': c_name[:3].upper(), 'country': 'TR'}
        )
    print(f"Seeded {len(cities)} cities.")
    
    sectors = ['Technology', 'Finance', 'retail']
    for s_name in sectors:
        Sector.objects.get_or_create(
            name=s_name,
            defaults={'code': s_name[:3].upper()}
        )
    print(f"Seeded {len(sectors)} sectors.")

except ImportError:
    pass
except Exception as e:
    print(f"Catalog seed error: {e}")

# Seed Credits
try:
    from apps.ledger.models import CreditPackage
    from apps.accounts.models import Organization
    
    org = Organization.objects.get(name='Test Org')
    created = False
    cp, created = CreditPackage.objects.get_or_create(organization=org)
    if created or cp.balance < 10000:
        cp.balance = 10000
        cp.save()
        print(f"Set balance for {org.name} to 10000.")
except ImportError:
    pass
except Exception as e:
    print(f"Credit seed error: {e}")
