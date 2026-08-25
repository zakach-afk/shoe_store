import re
from urllib.parse import quote
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import path
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
        return mark_safe('<span class="text-xs text-gray-400 font-bold">Upload to preview</span>')


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
            '{} Products</span>', str(count)
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
                '<div><strong class="text-gray-900 dark:text-gray-100 block text-xs font-bold uppercase">{}</strong>'
                '<span class="text-[10px] text-gray-500 font-mono">ID: #{}</span></div>'
                '</div>',
                first_img.image.url, obj.name, obj.name, str(obj.id)
            )
        return mark_safe(
            '<div class="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center text-gray-400 text-xs font-bold border">NO IMG</div>'
        )

    @display(description="Pricing (PKR)")
    def price_display(self, obj):
        price = obj.active_price
        price_str = f"Rs. {float(price or 0):,.2f}"
        return format_html('<span class="font-bold text-gray-900 dark:text-gray-100 text-sm">{}</span>', price_str)

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
    fields = ('item_preview', 'product_display', 'size_badge', 'quantity_badge', 'price_display', 'line_total')
    readonly_fields = ('item_preview', 'product_display', 'size_badge', 'quantity_badge', 'price_display', 'line_total')

    @display(description="Product Photo")
    def item_preview(self, obj):
        img_url = ""
        if obj.product_image_url:
            img_url = obj.product_image_url
        elif obj.product:
            first_img = obj.product.images.first()
            if first_img and first_img.image:
                img_url = first_img.image.url
        
        # Fallback search if still missing
        if not img_url:
            name = obj.product_name or (obj.product.name if obj.product else "")
            clean = re.sub(r'^\d+\s*x\s*', '', name)
            clean = re.sub(r'\s*\(Size.*?\)', '', clean).strip()
            if clean:
                p = Product.objects.filter(name__icontains=clean).first()
                if p:
                    f = p.images.first()
                    if f and f.image:
                        img_url = f.image.url

        if img_url:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" class="w-16 h-16 object-cover rounded-xl border border-gray-200 dark:border-gray-700 shadow-md hover:scale-105 transition transform" alt="Product" />'
                '</a>',
                img_url, img_url
            )
        return mark_safe('<div class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center text-[10px] text-gray-400 font-bold border">NO IMG</div>')

    @display(description="Product Name")
    def product_display(self, obj):
        name = obj.product_name or (obj.product.name if obj.product else "Footwear Item")
        if obj.product:
            return format_html(
                '<div class="flex flex-col">'
                '<a href="/admin/products/product/{}/change/" class="font-bold text-blue-600 hover:underline text-xs uppercase">{}</a>'
                '<span class="text-[10px] text-gray-400 font-mono">Product ID: #{}</span>'
                '</div>',
                str(obj.product.id), name, str(obj.product.id)
            )
        return format_html('<strong class="text-gray-900 dark:text-gray-100 text-xs uppercase">{}</strong>', name)

    @display(description="Size & Variant")
    def size_badge(self, obj):
        return format_html(
            '<span class="inline-flex items-center px-3 py-1 rounded-lg text-xs font-bold bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700">'
            '{}</span>',
            str(obj.size)
        )

    @display(description="Qty")
    def quantity_badge(self, obj):
        return format_html(
            '<span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-black bg-blue-100 text-blue-800">'
            '{}x</span>',
            str(obj.quantity)
        )

    @display(description="Unit Price")
    def price_display(self, obj):
        if not obj or obj.price is None:
            return mark_safe('<span class="text-xs text-gray-400 font-semibold">Rs. 0.00</span>')
        try:
            p = float(obj.price)
        except (ValueError, TypeError):
            p = 0.0
        price_str = f"Rs. {p:,.2f}"
        return format_html('<span class="text-xs text-gray-600 dark:text-gray-400 font-semibold">{}</span>', price_str)

    @display(description="Subtotal")
    def line_total(self, obj):
        if not obj or obj.price is None:
            return mark_safe('<span class="font-black text-gray-900 dark:text-gray-100 text-sm">Rs. 0.00</span>')
        try:
            p = float(obj.price)
            q = int(obj.quantity or 1)
        except (ValueError, TypeError):
            p = 0.0
            q = 1
        sub = p * q
        sub_str = f"Rs. {sub:,.2f}"
        return format_html('<span class="font-black text-gray-900 dark:text-gray-100 text-sm">{}</span>', sub_str)


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
    readonly_fields = ('created_at', 'customer_quick_actions', 'status_quick_changer', 'order_summary_header')

    fieldsets = (
        ("Order Status & 1-Click Action", {
            "fields": ("status_quick_changer", "status", "order_summary_header"),
        }),
        ("Customer & Delivery Details", {
            "fields": ("customer_quick_actions", "full_name", "phone_number", "city", "shipping_address", "total_amount", "created_at"),
        }),
    )

    actions = ['mark_dispatched', 'mark_delivered', 'mark_cancelled', 'mark_pending']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/set-status/<str:new_status>/', self.admin_site.admin_view(self.set_order_status), name='order_set_status'),
        ]
        return custom_urls + urls

    def set_order_status(self, request, order_id, new_status):
        order = get_object_or_404(Order, pk=order_id)
        if new_status in ['Pending', 'Dispatched', 'Delivered', 'Cancelled']:
            order.status = new_status
            order.save()
            messages.success(request, f"✨ Order #SL-{order.id:06d} status changed to '{new_status}' successfully!")
        return redirect(request.META.get('HTTP_REFERER', f'/admin/products/order/{order_id}/change/'))

    @display(description="Order ID")
    def order_id_badge(self, obj):
        order_str = f"#SL-{obj.id:06d}"
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="font-mono font-extrabold text-blue-700 bg-blue-50 px-3 py-1 rounded-lg text-xs border border-blue-200 shadow-sm">'
            '{}</span>'
            '</div>',
            order_str
        )

    @display(description="Customer")
    def customer_info(self, obj):
        name = str(obj.full_name or "Guest Customer")
        phone = str(obj.phone_number or "No Phone")
        return format_html(
            '<div class="flex flex-col">'
            '<strong class="text-gray-900 dark:text-gray-100 font-bold text-xs uppercase">{}</strong>'
            '<span class="text-xs text-gray-500 font-mono">📞 {}</span>'
            '</div>',
            name, phone
        )

    @display(description="WhatsApp Action")
    def whatsapp_direct_action(self, obj):
        clean_phone = re.sub(r'\D', '', str(obj.phone_number or ''))
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        
        name = str(obj.full_name or "Customer")
        total = float(obj.total_amount or 0)
        wa_msg = quote(f"Hello {name}, this is SOLO Footwear regarding your Order #SL-{obj.id:06d} (Total: Rs. {total:,.2f}). We are processing your parcel for delivery!")
        return format_html(
            '<a href="https://wa.me/{}?text={}" target="_blank" class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-lg bg-[#25D366] hover:bg-[#20bd5a] text-white text-xs font-bold shadow transition" title="Open WhatsApp Chat">'
            '<span>💬 WhatsApp</span>'
            '</a>',
            clean_phone, wa_msg
        )

    @display(description="Ordered Items")
    def order_items_preview(self, obj):
        items = list(obj.items.all())
        if not items:
            return mark_safe('<span class="text-gray-400 text-xs">No items</span>')
        first_item = items[0]
        extra_count = len(items) - 1
        name = first_item.product_name or (first_item.product.name if first_item.product else "Footwear Item")
        extra_badge = f' (+{extra_count} more)' if extra_count > 0 else ''
        summary_str = f"{first_item.quantity}x {name} ({first_item.size}){extra_badge}"
        return format_html(
            '<div class="text-xs text-gray-800 dark:text-gray-200 font-medium truncate max-w-[220px]" title="{}">'
            '{}'
            '</div>',
            summary_str, summary_str
        )

    @display(description="Total Amount")
    def formatted_total(self, obj):
        total = float(obj.total_amount or 0)
        total_str = f"Rs. {total:,.2f}"
        return format_html(
            '<span class="font-extrabold text-blue-700 dark:text-blue-400 text-sm">{}</span>',
            total_str
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
            style, str(obj.status or "Pending")
        )

    @display(description="⚡ 1-Click Status Changer")
    def status_quick_changer(self, obj):
        if not obj.id:
            return ""
        cur = obj.status or 'Pending'
        p_class = "bg-amber-500 text-white ring-2 ring-amber-300 font-black shadow" if cur == 'Pending' else "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-amber-100"
        d_class = "bg-blue-600 text-white ring-2 ring-blue-300 font-black shadow" if cur == 'Dispatched' else "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-blue-100"
        dl_class = "bg-emerald-600 text-white ring-2 ring-emerald-300 font-black shadow" if cur == 'Delivered' else "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-emerald-100"
        c_class = "bg-rose-600 text-white ring-2 ring-rose-300 font-black shadow" if cur == 'Cancelled' else "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-rose-100"

        order_id_str = str(obj.id)
        return format_html(
            '<div class="flex flex-wrap items-center gap-3 p-4 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl my-2 shadow-sm">'
            '<span class="text-xs font-bold text-gray-600 dark:text-gray-400 uppercase tracking-wider">Click to Switch Status Instantly:</span>'
            '<div class="flex items-center space-x-2">'
            '<a href="/admin/products/order/{}/set-status/Pending/" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition {}">⏳ Pending</a>'
            '<a href="/admin/products/order/{}/set-status/Dispatched/" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition {}">🚚 Mark Dispatched</a>'
            '<a href="/admin/products/order/{}/set-status/Delivered/" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition {}">✅ Mark Delivered</a>'
            '<a href="/admin/products/order/{}/set-status/Cancelled/" class="px-3.5 py-1.5 rounded-xl text-xs font-bold transition {}">❌ Cancel Order</a>'
            '</div>'
            '</div>',
            order_id_str, p_class,
            order_id_str, d_class,
            order_id_str, dl_class,
            order_id_str, c_class
        )

    @display(description="⚡ Quick Customer Contact")
    def customer_quick_actions(self, obj):
        if not obj.id:
            return "Save order first."
        clean_phone = re.sub(r'\D', '', str(obj.phone_number or ''))
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        
        name = str(obj.full_name or "Customer")
        total = float(obj.total_amount or 0)
        wa_msg = quote(f"Hello {name}, this is SOLO Footwear regarding your Order #SL-{obj.id:06d} for Rs. {total:,.2f}. How can we assist you?")
        wa_url = f"https://wa.me/{clean_phone}?text={wa_msg}"
        
        return format_html(
            '<div class="flex flex-wrap items-center gap-3 p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl my-2">'
            '<a href="{}" target="_blank" class="inline-flex items-center space-x-2 bg-[#25D366] hover:bg-[#20bd5a] text-white px-4 py-2 rounded-xl text-xs font-bold shadow transition">'
            '<span>💬 Chat with Customer on WhatsApp</span>'
            '</a>'
            '<a href="tel:{}" class="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-xs font-bold shadow transition">'
            '<span>📞 Call Customer Phone</span>'
            '</a>'
            '<span class="text-xs text-gray-500 font-medium">Payment Mode: <strong>Cash on Delivery (Open Parcel)</strong></span>'
            '</div>',
            wa_url, str(obj.phone_number or '')
        )

    @display(description="Order Financial Summary")
    def order_summary_header(self, obj):
        if not obj.id:
            return ""
        order_ref_str = f"#SL-{obj.id:06d}"
        total = float(obj.total_amount or 0)
        total_str = f"Rs. {total:,.2f}"
        return format_html(
            '<div class="p-4 bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 rounded-2xl my-2 flex items-center justify-between shadow-sm">'
            '<div>'
            '<span class="text-[11px] text-blue-900 dark:text-blue-300 font-bold uppercase tracking-wider block">Order Reference</span>'
            '<strong class="text-base text-blue-900 dark:text-blue-100 font-mono">{}</strong>'
            '</div>'
            '<div class="text-right">'
            '<span class="text-[11px] text-blue-900 dark:text-blue-300 font-bold uppercase tracking-wider block">Total Payable</span>'
            '<strong class="text-2xl text-blue-700 dark:text-blue-400 font-black">{}</strong>'
            '</div>'
            '</div>',
            order_ref_str, total_str
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
        clean_phone = re.sub(r'\D', '', str(obj.phone))
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
        clean_phone = re.sub(r'\D', '', str(obj.phone))
        if clean_phone.startswith('0'):
            clean_phone = '92' + clean_phone[1:]
        elif not clean_phone.startswith('92'):
            clean_phone = '92' + clean_phone
        wa_msg = quote(f"Hello {obj.name}, thank you for contacting SOLO Footwear. Regarding your message: '{obj.comment}'")
        return format_html(
            '<div class="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-900 border rounded-xl my-2">'
            '<a href="https://wa.me/{}?text={}" target="_blank" class="inline-flex items-center space-x-2 bg-[#25D366] text-white px-4 py-2 rounded-xl text-xs font-bold shadow hover:bg-[#20bd5a] transition">'
            '<span>💬 Send Reply via WhatsApp</span>'
            '</a>'
            '<a href="tel:{}" class="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-bold shadow hover:bg-blue-700 transition">'
            '<span>📞 Call Customer</span>'
            '</a>'
            '</div>',
            clean_phone, wa_msg, str(obj.phone)
        )
