from django.db import migrations

def create_loro_piana_category(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    lp_cat, _ = Category.objects.get_or_create(
        slug='loro-piana',
        defaults={'name': 'Loro Piana', 'order': 3}
    )
    Product.objects.filter(name__icontains='Loro Piana').update(category=lp_cat)

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_productreview'),
    ]

    operations = [
        migrations.RunPython(create_loro_piana_category, migrations.RunPython.noop),
    ]
