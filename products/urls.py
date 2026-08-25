from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('size-guide/', views.size_guide, name='size_guide'),
    path('pages/size-guide/', views.size_guide, name='size_guide_alt'),
    path('faqs/', views.faqs, name='faqs'),
    path('pages/faqs/', views.faqs, name='faqs_alt'),
    path('contact/', views.contact, name='contact'),
    path('pages/contact/', views.contact, name='contact_alt'),
    path('order-cancellation/', views.order_cancellation, name='order_cancellation'),
    path('pages/order-cancellation/', views.order_cancellation, name='order_cancellation_alt'),
    path('shoe-care-tips/', views.shoe_care_tips, name='shoe_care_tips'),
    path('pages/shoe-care-tips/', views.shoe_care_tips, name='shoe_care_tips_alt'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('pages/shipping-policy/', views.shipping_policy, name='shipping_policy_alt'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('policies/refund-policy/', views.refund_policy, name='refund_policy_policy'),
    path('pages/refund-policy/', views.refund_policy, name='refund_policy_alt'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('policies/terms-of-service/', views.terms_of_service, name='terms_of_service_policy'),
    path('pages/terms-of-service/', views.terms_of_service, name='terms_of_service_alt'),
    path('terms/', views.terms_of_service, name='terms'),
    path('api/place-order/', views.api_place_order, name='api_place_order'),
    path('api/submit-review/', views.api_submit_review, name='api_submit_review'),
    path('api/reviews/', views.api_get_reviews, name='api_get_reviews'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
]