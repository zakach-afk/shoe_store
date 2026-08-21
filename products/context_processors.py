from .models import Category, Product

def categories_processor(request):
    """
    Makes categories and drawer featured products globally available
    across all templates (header, main page, mobile drawer, footer).
    """
    return {
        'categories': Category.objects.all(),
        'drawer_featured_products': Product.objects.filter(is_active=True, is_featured=True)[:6],
    }