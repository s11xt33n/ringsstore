"""
Админка для моделей shop.
"""
from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для продуктов."""
    list_display = ['name', 'ring_type', 'material', 'price', 'created_at']
    list_filter = ['ring_type', 'material', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов."""
    list_display = ['id', 'customer_name', 'product', 'ring_size', 'status', 'quantity', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'email', 'phone', 'ring_size']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status']  # Можно менять статус прямо из списка

