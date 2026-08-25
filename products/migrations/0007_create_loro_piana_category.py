from django.db import migrations

def clear_all_fake_and_test_reviews(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    ProductReview = apps.get_model('products', 'ProductReview')
    
    casuals_cat = Category.objects.filter(slug='casuals').first()
    if casuals_cat:
        Product.objects.filter(category__slug='loro-piana').update(category=casuals_cat)
    Category.objects.filter(slug='loro-piana').delete()
    
    # Clear all test/fake reviews so only 100% genuine customer reviews will be stored
    ProductReview.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_productreview'),
    ]

    operations = [
        migrations.RunPython(clear_all_fake_and_test_reviews, migrations.RunPython.noop),
    ]
