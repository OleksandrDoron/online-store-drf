from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Category name")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ("id",)


class Product(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Product name")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Category"
    )
    price = models.DecimalField(
        default=0.00, max_digits=6, decimal_places=2, verbose_name="Price"
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity")
    discount = models.IntegerField(
        default=0, null=True, blank=True, verbose_name="Discount"
    )
    available = models.BooleanField(default=True, verbose_name="Availability")
    cost_price = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name="Cost Price"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Create at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Update at")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ("id",)
