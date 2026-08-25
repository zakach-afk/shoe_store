from django.db.models import Avg
from .models import Category, Product, ProductReview

def categories_processor(request):
    """
    Makes categories, featured products, recommended items, and customer reviews globally available
    across all templates (header, main page, mobile drawer, quick view modal, footer).
    """
    approved_reviews = ProductReview.objects.filter(is_approved=True)
    reviews_count = approved_reviews.count()
    avg_data = approved_reviews.aggregate(Avg('rating'))['rating__avg']
    reviews_avg = round(avg_data, 1) if avg_data else 0

    return {
        'categories': Category.objects.exclude(slug='loro-piana').order_by('order', 'name'),
        'drawer_featured_products': Product.objects.filter(is_active=True, is_featured=True)[:8],
        'all_recommended_products': Product.objects.filter(is_active=True).prefetch_related('images')[:12],
        'recent_reviews': approved_reviews.order_by('-created_at')[:10],
        'reviews_count': reviews_count,
        'reviews_avg': reviews_avg,
    }