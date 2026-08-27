from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_solofootwear_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    hashed_pwd = make_password('wariseli13254')
    
    user, created = User.objects.get_or_create(
        username='Solofootwear',
        defaults={'is_staff': True, 'is_superuser': True, 'password': hashed_pwd}
    )
    if not created:
        user.password = hashed_pwd
        user.is_staff = True
        user.is_superuser = True
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_populate_product_descriptions'),
    ]

    operations = [
        migrations.RunPython(create_solofootwear_superuser),
    ]
