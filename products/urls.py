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
    path('api/place-order/', views.api_place_order, name='api_place_order'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
]