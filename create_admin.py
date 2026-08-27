import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

# Ensure 'zaka' superuser exists
u, created = User.objects.get_or_create(
    username='zaka',
    defaults={'email': 'warisali942015@gmail.com', 'is_staff': True, 'is_superuser': True}
)
u.set_password('soloshoes2026')
u.is_staff = True
u.is_superuser = True
u.save()

# Ensure 'admin' superuser exists
u_admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@solofootwear.com', 'is_staff': True, 'is_superuser': True}
)
u_admin.set_password('soloshoes2026')
u_admin.is_staff = True
u_admin.is_superuser = True
u_admin.save()

print("Superusers configured successfully!")
