from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ("id",)


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )
    price = models.DecimalField(
        default=0.00, max_digits=6, decimal_places=2, verbose_name="Цена"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    discount = models.FloatField(
        default=0.00, null=True, blank=True, verbose_name="Скидка"
    )
    available = models.BooleanField(default=True, verbose_name="Наличие")
    cost_price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Себестоимость"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ("id",)
