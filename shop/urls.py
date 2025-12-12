"""
URLs для приложения shop.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.index, name='index'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('order/success/<int:order_id>/', views.order_success, name='order_success'),
    path('orders/', views.orders_list, name='orders_list'),
    
    # API endpoints
    path('api/products/', views.api_products, name='api_products'),
    path('api/orders/', views.api_create_order, name='api_create_order'),
]

