from django.contrib import admin
from store.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "quantity",
        "discount",
        "available",
        "cost_price",
        "created_at",
        "updated_at",
    )
    list_filter = ("category", "available", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("id",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "category",
                    "price",
                    "quantity",
                    "discount",
                    "available",
                    "cost_price",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")
