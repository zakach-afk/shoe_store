from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category


def home(request):
    categories = Category.objects.all().order_by('order', 'name')
    products = Product.objects.filter(is_active=True).prefetch_related('images')
    
    peshawari_products = Product.objects.filter(category__slug='peshawari-chappals', is_active=True).prefetch_related('images')[:4]
    formals_products = Product.objects.filter(category__slug='formals', is_active=True).prefetch_related('images')[:4]
    casuals_products = Product.objects.filter(category__slug='casuals', is_active=True).prefetch_related('images')[:4]
    chelsea_products = Product.objects.filter(category__slug='chelsea', is_active=True).prefetch_related('images')[:4]
    
    context = {
        'categories': categories,
        'products': products,
        'peshawari_products': peshawari_products,
        'formals_products': formals_products,
        'casuals_products': casuals_products,
        'chelsea_products': chelsea_products,
    }
    return render(request, 'products/home.html', context)


def category_detail(request, slug):
    categories = Category.objects.all().order_by('order', 'name')
    category = get_object_or_404(Category, slug=slug)
    
    products = Product.objects.filter(category=category, is_active=True).prefetch_related('images')
        
    context = {
        'categories': categories,
        'current_category': category,
        'products': products,
    }
    return render(request, 'products/category_detail.html', context)


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









import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Order, OrderItem

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
                return JsonResponse({'success': False, 'error': 'Please fill in all required delivery fields.'}, status=400)
            
            total_amount = 0
            for item in items_data:
                price = float(item.get('price', 0))
                qty = int(item.get('qty', 1))
                total_amount += (price * qty)
                
            # Create Order in DB
            order = Order.objects.create(
                full_name=full_name,
                phone_number=phone_number,
                city=city,
                shipping_address=shipping_address,
                total_amount=total_amount,
                status='Pending'
            )
            
            # Create OrderItems
            for item in items_data:
                product_name = item.get('name', '')
                size = item.get('size', '7/40')
                color = item.get('color', 'Black')
                qty = int(item.get('qty', 1))
                price = float(item.get('price', 0))
                
                matched_product = Product.objects.filter(name__icontains=product_name).first()
                
                OrderItem.objects.create(
                    order=order,
                    product=matched_product,
                    size=f"{size} ({color})" if color else f"{size}",
                    quantity=qty,
                    price=price
                )
                
            return JsonResponse({
                'success': True,
                'order_id': f"SL-{order.id:06d}",
                'message': 'Order placed successfully!'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)