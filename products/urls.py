from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/place-order/', views.api_place_order, name='api_place_order'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
]