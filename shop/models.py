"""
Модели для системы заказа обручальных и помолвочных колец.
"""
from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Модель продукта (кольцо).
    """
    RING_TYPE_CHOICES = [
        ('wedding', 'Обручальное кольцо'),
        ('engagement', 'Помолвочное кольцо'),
    ]
    
    MATERIAL_CHOICES = [
        ('gold', 'Золото'),
        ('silver', 'Серебро'),
        ('platinum', 'Платина'),
        ('white_gold', 'Белое золото'),
        ('rose_gold', 'Розовое золото'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название кольца'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Подробное описание кольца'
    )
    ring_type = models.CharField(
        max_length=20,
        choices=RING_TYPE_CHOICES,
        verbose_name='Тип кольца',
        help_text='Обручальное или помолвочное'
    )
    material = models.CharField(
        max_length=20,
        choices=MATERIAL_CHOICES,
        verbose_name='Материал',
        help_text='Материал изготовления'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        validators=[MinValueValidator(0)],
        help_text='Цена в рублях'
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Изображение',
        help_text='Фото кольца (опционально)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Order(models.Model):
    """
    Модель заказа.
    """
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('done', 'Выполнен'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Продукт'
    )
    customer_name = models.CharField(
        max_length=100,
        verbose_name='Имя клиента'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    ring_size = models.CharField(
        max_length=10,
        verbose_name='Размер кольца',
        help_text='Размер кольца (например, 16, 17, 18)'
    )
    engraving_text = models.TextField(
        blank=True,
        null=True,
        verbose_name='Текст для гравировки',
        help_text='Текст, который будет нанесен на кольцо (опционально)'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='Количество',
        help_text='Количество колец'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} - {self.customer_name}'

