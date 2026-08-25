from django.db import migrations

def remove_loro_piana_category(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    casuals_cat = Category.objects.filter(slug='casuals').first()
    if casuals_cat:
        Product.objects.filter(category__slug='loro-piana').update(category=casuals_cat)
    Category.objects.filter(slug='loro-piana').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_productreview'),
    ]

    operations = [
        migrations.RunPython(remove_loro_piana_category, migrations.RunPython.noop),
    ]
