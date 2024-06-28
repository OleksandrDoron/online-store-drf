from decimal import Decimal
from typing import Union
from rest_framework import serializers
from mixins import DiscountPriceMixin
from validators import validate_price


# Serializer for listing products.
class ProductSearchSerializer(DiscountPriceMixin, serializers.Serializer):
    name = serializers.CharField(read_only=True)
    price = serializers.FloatField(read_only=True)
    discount = serializers.IntegerField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)


# Serializer for retrieving a product.
class ProductDetailSerializer(DiscountPriceMixin, serializers.Serializer):
    name = serializers.CharField(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price = serializers.FloatField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)
    discount = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    category_id = serializers.IntegerField(
        help_text="ID of the category. Use the 'v1/categories/search' endpoint to get available categories.",
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    available = serializers.BooleanField(default=True)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def validate(
        self, attrs: dict[str, Union[Decimal, int]]
    ) -> dict[str, Union[Decimal, int]]:
        """
        Validates the product price after applying a discount to ensure it does not fall below its cost price.
        """
        cost_price = attrs["cost_price"]
        price = attrs["price"]
        discount = attrs["discount"]

        validate_price(
            cost_price, price, discount
        )  # Call a function that checks the correctness of the price.
        return attrs


class ProductPartialUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50, required=False)
    category_id = serializers.IntegerField(
        help_text="ID of the category. Use the /categories/ endpoint to get available categories.",
        required=False,
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    quantity = serializers.IntegerField(required=False)
    discount = serializers.IntegerField(default=0, required=False)
    available = serializers.BooleanField(default=True, required=False)
    cost_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )

    def validate(
        self, attrs: dict[str, Union[Decimal, int]]
    ) -> dict[str, Union[Decimal, int]]:
        """
        Validates the product attributes during a partial update to ensure the price after applying a discount
        does not fall below the cost price.
        """
        instance = self.instance
        cost_price = attrs.get("cost_price", instance.cost_price)
        price = attrs.get("price", instance.price)
        discount = attrs.get("discount", instance.discount)

        validate_price(
            cost_price, price, discount
        )  # Call a function that checks the correctness of the price.
        return attrs


# Serializer for handling Create, Read, and Delete operations on Category objects.
class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
