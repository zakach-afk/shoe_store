from django.db import migrations

def clear_fake_reviews_and_cleanup_category(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    ProductReview = apps.get_model('products', 'ProductReview')
    
    casuals_cat = Category.objects.filter(slug='casuals').first()
    if casuals_cat:
        Product.objects.filter(category__slug='loro-piana').update(category=casuals_cat)
    Category.objects.filter(slug='loro-piana').delete()
    
    # Remove fake seeded reviews
    ProductReview.objects.filter(customer_name__in=['Muhammad Usman', 'Hamza Tariq', 'Zubair Ahmed', 'Khurram Shahzad', 'Farhan Malik']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_productreview'),
    ]

    operations = [
        migrations.RunPython(clear_fake_reviews_and_cleanup_category, migrations.RunPython.noop),
    ]
