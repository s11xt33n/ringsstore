"""
Views для приложения shop.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Product, Order
from .forms import OrderForm


def index(request):
    """
    Главная страница - список всех продуктов.
    """
    products = Product.objects.all()
    return render(request, 'shop/index.html', {'products': products})


def product_detail(request, product_id):
    """
    Страница деталей продукта с формой заказа.
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.product = product
            order.save()
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm()
    
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'form': form
    })


def order_success(request, order_id):
    """
    Страница успешного создания заказа.
    """
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_success.html', {'order': order})


def orders_list(request):
    """
    Страница со списком всех заказов (для админа, без авторизации).
    """
    orders = Order.objects.all().select_related('product')
    return render(request, 'shop/orders_list.html', {'orders': orders})


# API Views

@require_http_methods(["GET"])
def api_products(request):
    """
    API endpoint: GET /api/products/
    Возвращает список всех продуктов в формате JSON.
    """
    products = Product.objects.all()
    products_data = []
    
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': str(product.price),
            'image': product.image.url if product.image else None,
            'created_at': product.created_at.isoformat(),
        })
    
    return JsonResponse({'products': products_data}, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def api_create_order(request):
    """
    API endpoint: POST /api/orders/
    Создает новый заказ из JSON данных.
    
    Ожидаемый JSON:
    {
        "product_id": 1,
        "customer_name": "Иван Иванов",
        "email": "ivan@example.com",
        "phone": "+79991234567",
        "custom_text": "Мой текст",
        "quantity": 2
    }
    """
    try:
        data = json.loads(request.body)
        
        # Получаем продукт
        product = get_object_or_404(Product, id=data.get('product_id'))
        
        # Создаем заказ
        order = Order.objects.create(
            product=product,
            customer_name=data.get('customer_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            ring_size=data.get('ring_size'),
            engraving_text=data.get('engraving_text', ''),
            quantity=data.get('quantity', 1),
        )
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': 'Заказ успешно создан'
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Неверный формат JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

