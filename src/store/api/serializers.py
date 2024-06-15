from decimal import Decimal
from rest_framework import serializers
from config.constants import LOSS_FACTOR
from store import models as app_models


class ProductSearchSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price = serializers.FloatField(read_only=True)
    discounted_price = serializers.SerializerMethodField(read_only=True)
    discount = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def get_discounted_price(self, obj: app_models.Product):
        if obj.discount:
            return obj.price - (obj.price * obj.discount / 100)
        return None

    def to_representation(self, instance):
        """
        Remove irrelevant discount-related fields from the serialized data.
        """
        data = super().to_representation(instance)
        if data["discounted_price"] is None:
            data.pop("discounted_price", None)

        if data["discount"] is None:
            data.pop("discount", None)
        return data


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)


class BaseProductSerializer(serializers.Serializer):
    @staticmethod
    def validate_price_and_discount(attrs):
        """
        Validates the product price after applying a discount to ensure it does not fall below its cost price.
        """
        cost_price = Decimal(attrs.get("cost_price", 0))
        price = Decimal(attrs.get("price", 0))
        discount = Decimal(attrs.get("discount", 0))

        # Calculate the minimum acceptable price after discount
        min_acceptable_price = cost_price * LOSS_FACTOR
        price_after_discount = price * (1 - discount / 100)

        # Check if the price is below the cost price
        if price < cost_price:
            raise serializers.ValidationError(
                "Product price cannot be lower than the cost price."
            )
        # Check if the discounted price falls below the cost price
        if price_after_discount < min_acceptable_price:
            raise serializers.ValidationError(
                "Product price after applying discount cannot be lower than the cost price."
            )
        return attrs

    def validate(self, attrs):
        return self.validate_price_and_discount(attrs)


class ProductSerializer(BaseProductSerializer):
    name = serializers.CharField(max_length=50)
    category = serializers.CharField(max_length=25)
    price = serializers.FloatField()
    quantity = serializers.IntegerField()
    discount = serializers.IntegerField(default=0)
    available = serializers.BooleanField(default=True)
    cost_price = serializers.FloatField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")


class ProductPartialUpdateSerializer(BaseProductSerializer):
    name = serializers.CharField(max_length=50, required=False)
    category = serializers.CharField(read_only=True)
    price = serializers.FloatField(required=False)
    quantity = serializers.IntegerField(required=False)
    discount = serializers.IntegerField(default=0, required=False)
    available = serializers.BooleanField(default=True, required=False)
    cost_price = serializers.FloatField(required=False)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
