from django.db import migrations

def populate_descriptions(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    
    default_desc_template = """Looking for formal shoes for work, a wedding, graduation or other official event? SOLO brings its royal collection.

• Upper : imported Cow leather
• Lining : Anti-Bacterial synthetic leather lining
• Sole : Imported
• In Sole : Soft Jelly insole providing addition comfort at key pressure point of the foot.
• Finish : Italian Spray
• Made : Hand crafted
• Colour : {color}
• Occasion : Casual, events, and Casual meetings"""

    for p in Product.objects.all():
        if not p.description or 'Upper :' not in p.description:
            color_val = p.name.split()[-1].capitalize() if len(p.name.split()) > 0 else 'Black'
            p.description = default_desc_template.format(color=color_val)
            p.save()

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_create_loro_piana_category'),
    ]

    operations = [
        migrations.RunPython(populate_descriptions),
    ]
