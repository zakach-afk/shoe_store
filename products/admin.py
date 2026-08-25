from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Category, Product, ProductImage, ProductSize, Order, OrderItem, ContactMessage

# Customize Admin Dashboard Branding
admin.site.site_header = "SOLO FOOTWEAR Admin"
admin.site.site_title = "SOLO FOOTWEAR Control Center"
admin.site.index_title = "Store Management Dashboard"


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


class ProductSizeInline(TabularInline):
    model = ProductSize
    extra = 3


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'products_count', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name',)
    actions = ['delete_selected']

    @display(description="Total Products")
    def products_count(self, obj):
        count = obj.products.count()
        return format_html(
            '<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-black bg-[#123C91] text-white shadow-sm">'
            '{} Products</span>', count
        )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price_display', 'is_featured_badge', 'is_active_badge', 'created_at')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline, ProductImageInline]

    @display(description="Image")
    def image_preview(self, obj):
        first_img = obj.images.first()
        if first_img and first_img.image:
            return format_html(
                '<img src="{}" class="w-12 h-12 object-cover rounded-lg border border-gray-300 dark:border-gray-700 shadow-sm" alt="{}" />',
                first_img.image.url, obj.name
            )
        return format_html('<div class="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-500 dark:text-gray-400 text-xs font-bold">NO IMG</div>')

    @display(description="Pricing")
    def price_display(self, obj):
        if obj.sale_price:
            return format_html(
                '<div class="flex flex-col"><span class="font-bold text-blue-600 dark:text-blue-400">Rs. {}</span>'
                '<span class="text-xs text-gray-400 line-through">Rs. {}</span></div>',
                obj.sale_price, obj.regular_price
            )
        return format_html('<span class="font-bold text-gray-900 dark:text-gray-100">Rs. {}</span>', obj.regular_price)

    @display(description="Featured", boolean=True)
    def is_featured_badge(self, obj):
        return obj.is_featured

    @display(description="Active", boolean=True)
    def is_active_badge(self, obj):
        return obj.is_active


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('order_id_badge', 'full_name', 'phone_number', 'city', 'formatted_total', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'full_name', 'phone_number', 'city', 'shipping_address')
    list_editable = ()
    inlines = [OrderItemInline]
    readonly_fields = ('created_at',)

    @display(description="Order ID")
    def order_id_badge(self, obj):
        return format_html(
            '<span class="font-mono font-bold text-blue-700 dark:text-blue-300 bg-blue-100 dark:bg-blue-950 px-2.5 py-1 rounded text-xs border border-blue-200 dark:border-blue-800">#{}</span>',
            obj.id
        )

    @display(description="Total Amount")
    def formatted_total(self, obj):
        return format_html(
            '<span class="font-black text-blue-700 dark:text-blue-400">Rs. {}</span>',
            obj.total_amount
        )

    @display(description="Order Status")
    def status_badge(self, obj):
        badge_styles = {
            'Pending': 'bg-amber-500 text-white',
            'Dispatched': 'bg-blue-600 text-white',
            'Delivered': 'bg-emerald-600 text-white',
            'Cancelled': 'bg-rose-600 text-white',
        }
        style = badge_styles.get(obj.status, 'bg-gray-600 text-white')
        return format_html(
            '<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-black shadow-sm {}">'
            '{}</span>',
            style, obj.status
        )


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'comment_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'comment')
    readonly_fields = ('name', 'email', 'phone', 'comment', 'created_at')

    @display(description="Message Preview")
    def comment_short(self, obj):
        return obj.comment[:80] + '...' if len(obj.comment) > 80 else obj.comment