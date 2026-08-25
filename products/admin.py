import re
from urllib.parse import quote
from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display
from .models import Category, Product, ProductImage, ProductSize, Order, OrderItem, ContactMessage

# Admin Control Center Branding
admin.site.site_header = "SOLO FOOTWEAR Control Center"
admin.site.site_title = "SOLO FOOTWEAR Admin"
admin.site.index_title = "E-Commerce Management Dashboard"


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_preview', 'image', 'is_primary')
    readonly_fields = ('image_preview',)

    @display(description="Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" class="w-14 h-14 object-cover rounded-xl border border-gray-200 shadow-sm" alt="Image" />',
                obj.image.url
            )
        return format_html('<span class="text-xs text-gray-400 font-bold">Upload to preview</span>')


class ProductSizeInline(TabularInline):
    model = ProductSize
    extra = 3
    fields = ('size', 'stock')


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
            '<span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-black bg-blue-600 text-white shadow-sm">'
            '{} Products</span>', count
        )


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price_display', 'is_featured_badge', 'is_active_badge', 'created_at')
    list_filter = ('category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductSizeInline, ProductImageInline]
    actions = ['make_featured', 'make_active', 'make_inactive']

    @display(description="Product")
    def image_preview(self, obj):
        first_img = obj.images.first()
        if first_img and first_img.image:
            return format_html(
                '<div class="flex items-center space-x-3">'
                '<img src="{}" class="w-12 h-12 object-cover rounded-xl border border-gray-200 shadow-sm" alt="{}" />'
                '<div><strong class="text-gray-900 block text-xs font-bold uppercase">{}</strong>'
                '<span class="text-[10px] text-gray-500 font-mono">ID: #{}</span></div>'
                '</div>',
                first_img.image.url, obj.name, obj.name, obj.id
            )
        return format_html(
            '<div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-gray-400 text-xs font-bold border">NO IMG</div>'
        )

    @display(description="Pricing (PKR)")
    def price_display(self, obj):
        if obj.sale_price:
            return format_html(
                '<div class="flex flex-col"><span class="font-extrabold text-blue-600 text-sm">Rs. {:,.2f}</span>'
                '<span class="text-xs text-gray-400 line-through">Rs. {:,.2f}</span></div>',
                obj.sale_price, obj.regular_price
            )
        return format_html('<span class="font-bold text-gray-900 text-sm">Rs. {:,.2f}</span>', obj.regular_price)

    @display(description="Featured", boolean=True)
    def is_featured_badge(self, obj):
        return obj.is_featured

    @display(description="Active", boolean=True)
    def is_active_badge(self, obj):
        return obj.is_active

    @admin.action(description="Mark selected as Featured ⭐")
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f"{updated} products marked as featured.")

    @admin.action(description="Activate selected products ✅")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} products activated.")

    @admin.action(description="Deactivate selected products ⏸️")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} products deactivated.")


# --- ORDER MANAGEMENT ---

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    fields = ('item_preview', 'product', 'size', 'quantity', 'price', 'line_total')
    readonly_fields = ('item_preview', 'product', 'size', 'quantity', 'price', 'line_total')

    @display(description="Item")
    def item_preview(self, obj):
        if obj.product:
            first_img = obj.product.images.first()
            if first_img and first_img.image:
                return format_html(
                    '<img src="{}" class="w-12 h-12 object-cover rounded-xl border shadow-sm" alt="{}" />',
                    first_img.image.url, obj.product.name
                )
        return format_html('<div class="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-[10px] text-gray-400 font-bold border">NO IMG</div>')

    @display(description="Subtotal")
    def line_total(self, obj):
        sub = obj.price * obj.quantity
        return format_html('<span class="font-bold text-gray-900">Rs. {:,.2f}</span>', sub)


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'order_id_badge',
        'customer_info',
        'whatsapp_direct_action',
        'city',
        'order_items_preview',
        'formatted_total',
        'status_badge',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'city')
    search_fields = ('id', 'full_name', 'phone_number', 'city', 'shipping_address')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'customer_quick_actions', 'order_summary_header')

    fieldsets = (
        ("Customer & Shipping Information", {
            "fields": ("customer_quick_actions", "full_name", "phone_number", "city", "shipping_address"),
            "classes": ["tab"],
        }),
        ("Order Financials & Lifecycle Status", {
            "fields": ("order_summary_header", "status", "total_amount", "created_at"),
            "classes": ["tab"],
        }),
    )

    actions = ['mark_dispatched', 'mark_delivered', 'mark_cancelled', 'mark_pending']

    @display(description="Order ID")
    def order_id_badge(self, obj):
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="font-mono font-extrabold text-blue-700 bg-blue-50 px-3 py-1 rounded-lg text-xs border border-blue-200 shadow-sm">'
            '#SL-{:06d}</span>'
            '</div>',
            obj.id
        )

    @display(description="Customer")
    def customer_info(self, obj):
        return format_html(
            '<div class="flex flex-col">'
            '<strong class="text-gray-900 font-bold text-xs uppercase">{}</strong>'
            '<span class="text-xs text-gray-500 font-mono">📞 {}</span>'
            '</div>',
            obj.full_name, obj.phone_number
        )

    @display(description="WhatsApp Action")
    def whatsapp_direct_action(self, obj):
        clean_phone = re.sub(r'\D', '', obj.phone_number)
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        
        wa_msg = quote(f"Hello {obj.full_name}, this is SOLO Footwear regarding your Order #SL-{obj.id:06d} (Total: Rs. {obj.total_amount:,.2f}). We are processing your parcel for delivery!")
        return format_html(
            '<a href="https://wa.me/{}?text={}" target="_blank" class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-[#25D366] hover:bg-[#20bd5a] text-white text-xs font-bold shadow transition" title="Open WhatsApp Chat">'
            '<span>💬 Chat</span>'
            '</a>',
            clean_phone, wa_msg
        )

    @display(description="Ordered Items")
    def order_items_preview(self, obj):
        items = list(obj.items.all())
        if not items:
            return format_html('<span class="text-gray-400 text-xs">No items</span>')
        first_item = items[0]
        extra_count = len(items) - 1
        name = first_item.product.name if first_item.product else "Item"
        extra_badge = f' <span class="bg-gray-200 text-gray-700 text-[10px] font-bold px-1.5 py-0.5 rounded">+{extra_count} more</span>' if extra_count > 0 else ''
        return format_html(
            '<div class="text-xs text-gray-800 font-medium truncate max-w-[200px]">'
            '<strong>{}x</strong> {} ({}){}'
            '</div>',
            first_item.quantity, name, first_item.size, format_html(extra_badge)
        )

    @display(description="Total Amount")
    def formatted_total(self, obj):
        return format_html(
            '<span class="font-extrabold text-blue-700 text-sm">Rs. {:,.2f}</span>',
            obj.total_amount
        )

    @display(description="Status")
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

    @display(description="⚡ Quick Customer Contact")
    def customer_quick_actions(self, obj):
        if not obj.id:
            return "Save order first."
        clean_phone = re.sub(r'\D', '', obj.phone_number)
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        
        wa_msg = quote(f"Hello {obj.full_name}, this is SOLO Footwear regarding your Order #SL-{obj.id:06d} for Rs. {obj.total_amount:,.2f}. How can we assist you?")
        wa_url = f"https://wa.me/{clean_phone}?text={wa_msg}"
        
        return format_html(
            '<div class="flex flex-wrap items-center gap-3 p-3 bg-slate-50 border border-slate-200 rounded-xl my-2">'
            '<a href="{}" target="_blank" class="inline-flex items-center space-x-2 bg-[#25D366] hover:bg-[#20bd5a] text-white px-4 py-2 rounded-xl text-xs font-bold shadow transition">'
            '<span>💬 Chat with Customer on WhatsApp</span>'
            '</a>'
            '<a href="tel:{}" class="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow transition">'
            '<span>📞 Call Customer Phone</span>'
            '</a>'
            '<span class="text-xs text-gray-500 font-medium">Payment Mode: <strong>Cash on Delivery (Open Parcel)</strong></span>'
            '</div>',
            wa_url, obj.phone_number
        )

    @display(description="Order Financial Summary")
    def order_summary_header(self, obj):
        if not obj.id:
            return ""
        return format_html(
            '<div class="p-3 bg-blue-50 border border-blue-200 rounded-xl my-2 flex items-center justify-between">'
            '<div>'
            '<span class="text-xs text-blue-900 font-bold uppercase tracking-wider block">Order Reference</span>'
            '<strong class="text-base text-blue-900 font-mono">#SL-{:06d}</strong>'
            '</div>'
            '<div class="text-right">'
            '<span class="text-xs text-blue-900 font-bold uppercase tracking-wider block">Total Payable</span>'
            '<strong class="text-xl text-blue-700 font-black">Rs. {:,.2f}</strong>'
            '</div>'
            '</div>',
            obj.id, obj.total_amount
        )

    # Bulk Actions
    @admin.action(description="🚚 Mark selected as Dispatched")
    def mark_dispatched(self, request, queryset):
        c = queryset.update(status='Dispatched')
        self.message_user(request, f"{c} order(s) marked as Dispatched.")

    @admin.action(description="✅ Mark selected as Delivered")
    def mark_delivered(self, request, queryset):
        c = queryset.update(status='Delivered')
        self.message_user(request, f"{c} order(s) marked as Delivered.")

    @admin.action(description="❌ Mark selected as Cancelled")
    def mark_cancelled(self, request, queryset):
        c = queryset.update(status='Cancelled')
        self.message_user(request, f"{c} order(s) marked as Cancelled.")

    @admin.action(description="⏳ Reset selected to Pending")
    def mark_pending(self, request, queryset):
        c = queryset.update(status='Pending')
        self.message_user(request, f"{c} order(s) reset to Pending.")


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ('name', 'phone', 'email', 'whatsapp_reply_btn', 'comment_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone', 'comment')
    readonly_fields = ('name', 'email', 'phone', 'comment', 'created_at', 'quick_reply_box')

    fieldsets = (
        ("Inquiry Message Details", {
            "fields": ("quick_reply_box", "name", "phone", "email", "comment", "created_at"),
        }),
    )

    @display(description="Message Preview")
    def comment_short(self, obj):
        return obj.comment[:75] + '...' if len(obj.comment) > 75 else obj.comment

    @display(description="WhatsApp Reply")
    def whatsapp_reply_btn(self, obj):
        clean_phone = re.sub(r'\D', '', obj.phone)
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        wa_msg = quote(f"Hello {obj.name}, thank you for reaching out to SOLO Footwear regarding: '{obj.comment[:60]}...' How can we assist you?")
        return format_html(
            '<a href="https://wa.me/{}?text={}" target="_blank" class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-[#25D366] text-white text-xs font-bold shadow hover:bg-[#20bd5a] transition">'
            '<span>💬 Reply</span>'
            '</a>',
            clean_phone, wa_msg
        )

    @display(description="⚡ Quick Customer Response")
    def quick_reply_box(self, obj):
        clean_phone = re.sub(r'\D', '', obj.phone)
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        wa_msg = quote(f"Hello {obj.name}, thank you for contacting SOLO Footwear. Regarding your message: '{obj.comment}'")
        return format_html(
            '<div class="flex items-center space-x-3 p-3 bg-slate-50 border rounded-xl my-2">'
            '<a href="https://wa.me/{}?text={}" target="_blank" class="inline-flex items-center space-x-2 bg-[#25D366] text-white px-4 py-2 rounded-xl text-xs font-bold shadow hover:bg-[#20bd5a] transition">'
            '<span>💬 Send Reply via WhatsApp</span>'
            '</a>'
            '<a href="tel:{}" class="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow hover:bg-blue-700 transition">'
            '<span>📞 Call Customer</span>'
            '</a>'
            '</div>',
            clean_phone, wa_msg, obj.phone
        )
