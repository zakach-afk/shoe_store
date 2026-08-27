import urllib.parse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.mail import send_mail
from .models import Product, Category, ProductReview, Order, OrderItem, ContactMessage


def home(request):
    categories = Category.objects.exclude(slug='loro-piana').order_by('order', 'name')
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    
    peshawari_products = Product.objects.filter(category__slug='peshawari-chappals', is_active=True).prefetch_related('images')[:8]
    formals_products = Product.objects.filter(category__slug='formals', is_active=True).prefetch_related('images')[:8]
    casuals_products = Product.objects.filter(category__slug='casuals', is_active=True).prefetch_related('images')[:8]
    chelsea_products = Product.objects.filter(category__slug='chelsea', is_active=True).prefetch_related('images')[:8]
    loro_piana_products = Product.objects.filter(Q(category__slug='loro-piana') | Q(name__icontains='Loro Piana'), is_active=True).prefetch_related('images')[:8]
    sandals_products = Product.objects.filter(category__slug='sandals', is_active=True).prefetch_related('images')[:8]
    skechers_products = Product.objects.filter(category__slug='skechers', is_active=True).prefetch_related('images')[:8]
    slippers_products = Product.objects.filter(category__slug='slippers', is_active=True).prefetch_related('images')[:8]
    
    context = {
        'categories': categories,
        'products': products,
        'peshawari_products': peshawari_products,
        'formals_products': formals_products,
        'casuals_products': casuals_products,
        'chelsea_products': chelsea_products,
        'loro_piana_products': loro_piana_products,
        'sandals_products': sandals_products,
        'skechers_products': skechers_products,
        'slippers_products': slippers_products,
    }
    return render(request, 'products/home.html', context)


def category_detail(request, slug):
    categories = Category.objects.exclude(slug='loro-piana').order_by('order', 'name')
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).prefetch_related('images')
        
    context = {
        'categories': categories,
        'current_category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)


def product_detail(request, slug):
    categories = Category.objects.exclude(slug='loro-piana').order_by('order', 'name')
    product = get_object_or_404(Product, slug=slug)
    
    related_products = []
    if product.category:
        related_products = list(Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id).prefetch_related('images')[:8])
    if len(related_products) < 4:
        extra = list(Product.objects.filter(is_active=True).exclude(id=product.id).prefetch_related('images')[:8])
        for p in extra:
            if p not in related_products and len(related_products) < 8:
                related_products.append(p)
                
    context = {
        'categories': categories,
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def checkout(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/checkout.html', context)


def size_guide(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/size_guide.html', context)


def faqs(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/faqs.html', context)


import urllib.parse
from django.core.mail import send_mail
from .models import ContactMessage


def contact(request):
    categories = Category.objects.all().order_by('order', 'name')
    success_msg = False
    whatsapp_url = ""
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        if name and email and comment:
            # 1. Save to Database for Admin review
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                comment=comment
            )
            
            # 2. Try sending email notification to store email
            try:
                send_mail(
                    subject=f"New Contact Message from {name} - SOLO Footwear",
                    message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{comment}",
                    from_email=None,
                    recipient_list=['warisali942015@gmail.com'],
                    fail_silently=True,
                )
            except Exception:
                pass
            
            # 3. Format WhatsApp direct link for instant forwarding
            wa_text = f"Hi SOLO Footwear,\n\n*New Website Inquiry*\n*Name:* {name}\n*Email:* {email}\n*Phone:* {phone}\n*Message:*\n{comment}"
            whatsapp_url = f"https://wa.me/923192255100?text={urllib.parse.quote(wa_text)}"
            success_msg = True

    context = {
        'categories': categories,
        'success_msg': success_msg,
        'whatsapp_url': whatsapp_url,
    }
    return render(request, 'products/contact.html', context)



def order_cancellation(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/order_cancellation.html', context)


def shoe_care_tips(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/shoe_care_tips.html', context)


def shipping_policy(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/shipping_policy.html', context)


def refund_policy(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/refund_policy.html', context)


def terms_of_service(request):
    categories = Category.objects.all().order_by('order', 'name')
    context = {
        'categories': categories,
    }
    return render(request, 'products/terms_of_service.html', context)










import json
import re
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem, Product

logger = logging.getLogger(__name__)

def _clean_price_val(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val_clean = re.sub(r'^[^\d]*', '', val)
        val_clean = val_clean.replace(',', '')
        val_clean = re.sub(r'[^\d.]', '', val_clean)
        try:
            return float(val_clean) if val_clean else 0.0
        except ValueError:
            return 0.0
    return 0.0

@csrf_exempt
def api_place_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            full_name = data.get('full_name', '').strip()
            phone_number = data.get('phone_number', '').strip()
            city = data.get('city', '').strip()
            shipping_address = data.get('shipping_address', '').strip()
            items_data = data.get('items', [])
            
            if not full_name or not phone_number or not shipping_address or not items_data:
                return JsonResponse({'success': False, 'error': 'Please fill in all required delivery fields and add items.'}, status=400)
            
            total_amount = 0.0
            parsed_items = []
            for item in items_data:
                price = _clean_price_val(item.get('price', 0))
                try:
                    qty = int(item.get('qty', 1))
                except (ValueError, TypeError):
                    qty = 1
                if qty < 1:
                    qty = 1
                total_amount += (price * qty)
                parsed_items.append({
                    'name': item.get('name', 'Footwear Item'),
                    'size': item.get('size', '7/40'),
                    'color': item.get('color', 'Black'),
                    'image': item.get('image', ''),
                    'qty': qty,
                    'price': price,
                })
                
            # Create Order in DB
            order = Order.objects.create(
                full_name=full_name,
                phone_number=phone_number,
                city=city,
                shipping_address=shipping_address,
                total_amount=total_amount,
                status='Pending'
            )
            
            # Create OrderItems with smart product matching & persistent image URLs
            for item in parsed_items:
                raw_name = str(item['name']).strip()
                # Clean name: strip "1x ", "(Size 9/42 (Tan / Camel))"
                clean_name = re.sub(r'^\d+\s*x\s*', '', raw_name, flags=re.IGNORECASE)
                clean_name = re.sub(r'\s*\(Size.*?\)', '', clean_name, flags=re.IGNORECASE).strip()
                
                size = item['size']
                color = item['color']
                qty = item['qty']
                price = item['price']
                image_url = str(item.get('image', '')).strip()
                
                # Smart product match
                matched_product = None
                if clean_name:
                    matched_product = Product.objects.filter(name__iexact=clean_name).first()
                    if not matched_product:
                        matched_product = Product.objects.filter(name__icontains=clean_name).first()
                    if not matched_product:
                        tokens = [t for t in clean_name.split() if len(t) > 2]
                        for t in tokens:
                            matched_product = Product.objects.filter(name__icontains=t).first()
                            if matched_product:
                                break
                                
                if matched_product and not image_url:
                    first_img = matched_product.images.first()
                    if first_img and first_img.image:
                        image_url = first_img.image.url
                        
                display_name = clean_name or (matched_product.name if matched_product else raw_name)
                
                OrderItem.objects.create(
                    order=order,
                    product=matched_product,
                    product_name=display_name,
                    product_image_url=image_url,
                    size=f"{size} ({color})" if color and color not in str(size) else f"{size}",
                    quantity=qty,
                    price=price
                )
            
            print(f"[ORDER PLACED] Order #{order.id} for {full_name} ({phone_number}) - Total: Rs. {total_amount}")
            
            # Instant Order Email Notification to Store Owner (warisali942015@gmail.com)
            try:
                items_summary = "\n".join([
                    f"- {item['name']} | Size: {item['size']} ({item['color']}) | Qty: {item['qty']} | Price: Rs. {item['price']:,.2f}"
                    for item in parsed_items
                ])
                
                clean_phone = re.sub(r'[^0-9]', '', phone_number)
                customer_wa_msg = f"Hi {full_name}, this is SOLO Footwear confirming your Order #SL-{order.id:06d} for Rs. {total_amount:,.2f}."
                customer_wa_link = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(customer_wa_msg)}"

                owner_wa_msg = f"🔔 NEW ORDER ALERT!\nOrder: SL-{order.id:06d}\nCustomer: {full_name} ({phone_number})\nCity: {city}\nItems:\n{items_summary}\nTotal: Rs. {total_amount:,.2f}"
                owner_wa_link = f"https://wa.me/923088406867?text={urllib.parse.quote(owner_wa_msg)}"

                order_email_body = (
                    f"🛒 NEW ORDER RECEIVED ON SOLO FOOTWEAR!\n\n"
                    f"Order ID: SL-{order.id:06d}\n"
                    f"Customer Name: {full_name}\n"
                    f"Phone Number: {phone_number}\n"
                    f"City: {city}\n"
                    f"Shipping Address: {shipping_address}\n\n"
                    f"ITEMS ORDERED:\n"
                    f"{items_summary}\n\n"
                    f"TOTAL AMOUNT: Rs. {total_amount:,.2f}\n\n"
                    f"📲 1-Click WhatsApp Alert to Owner (03088406867):\n{owner_wa_link}\n\n"
                    f"💬 1-Click Confirm with Customer on WhatsApp:\n{customer_wa_link}"
                )
                
                send_mail(
                    subject=f"🛒 NEW ORDER SL-{order.id:06d} from {full_name} ({city})",
                    message=order_email_body,
                    from_email=None,
                    recipient_list=['zakach6867@gmail.com', 'warisali942015@gmail.com'],
                    fail_silently=True,
                )
            except Exception as email_err:
                logger.error(f"Failed to send order email: {email_err}")

            return JsonResponse({
                'success': True,
                'order_id': f"SL-{order.id:06d}",
                'message': 'Order placed successfully!'
            })
            
        except Exception as e:
            print(f"[ORDER ERROR] Exception occurred while placing order: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Failed to process order: {str(e)}'
            }, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def api_submit_review(request):
    if request.method == 'POST':
        try:
            try:
                data = json.loads(request.body.decode('utf-8'))
            except (ValueError, TypeError):
                data = request.POST
                
            customer_name = str(data.get('name', '')).strip()
            city = str(data.get('city', 'Verified Customer')).strip()
            comment = str(data.get('comment', '')).strip()
            product_name = str(data.get('product_name', '')).strip()
            
            try:
                rating = int(data.get('rating', 5))
                if rating < 1 or rating > 5:
                    rating = 5
            except (ValueError, TypeError):
                rating = 5
                
            if not customer_name or not comment:
                return JsonResponse({'success': False, 'error': 'Please enter your name and review.'}, status=400)
                
            matched_product = None
            if product_name:
                matched_product = Product.objects.filter(name__icontains=product_name).first()
                
            review = ProductReview.objects.create(
                product=matched_product,
                product_name=product_name or (matched_product.name if matched_product else "SOLO Footwear Customer"),
                customer_name=customer_name,
                city=city or "Verified Customer",
                rating=rating,
                comment=comment,
                is_verified_purchase=True,
                is_approved=True
            )
            
            return JsonResponse({
                'success': True,
                'review': {
                    'id': review.id,
                    'name': review.customer_name,
                    'city': review.city,
                    'rating': review.rating,
                    'comment': review.comment,
                    'date': review.created_at.strftime('%d %b %Y'),
                    'verified': review.is_verified_purchase
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


def api_get_reviews(request):
    product_name = request.GET.get('product_name', '').strip()
    reviews = ProductReview.objects.filter(is_approved=True).order_by('-created_at')
    
    if product_name:
        exact_reviews = reviews.filter(
            Q(product__name__iexact=product_name) |
            Q(product_name__iexact=product_name)
        )
        if exact_reviews.exists():
            reviews = exact_reviews
        else:
            reviews = reviews.filter(
                Q(product__name__icontains=product_name) |
                Q(product_name__icontains=product_name)
            )
    else:
        reviews = reviews.none()
            
    reviews_list = []
    total_rating = 0
    for r in reviews[:30]:
        total_rating += r.rating
        reviews_list.append({
            'id': r.id,
            'name': r.customer_name,
            'city': r.city,
            'rating': r.rating,
            'comment': r.comment,
            'date': r.created_at.strftime('%d %b %Y'),
            'verified': r.is_verified_purchase
        })
    count = len(reviews_list)
    avg_rating = round(total_rating / count, 1) if count > 0 else 0
    return JsonResponse({
        'success': True,
        'reviews': reviews_list,
        'count': count,
        'avg_rating': avg_rating
    })