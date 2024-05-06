from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from store import models as app_models
from store.models import Product, Category


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    category = serializers.CharField(source="category.name", read_only=True)
    price = serializers.FloatField(read_only=True)
    discount_price = serializers.SerializerMethodField(read_only=True)
    discount = serializers.IntegerField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def get_discount_price(self, obj: app_models.Product):
        """Возвращает цену товара с учётом скидки, если скидка присутствует."""

        if obj.discount != Decimal("0.00"):
            discount_price = obj.price * (
                Decimal("1.00") - obj.discount / Decimal("100.00")
            )
            return discount_price
        else:
            return None

    def to_representation(self, instance):
        """Удаляет поля 'discount_price' и 'discount', если их значения соответственно равны None и 0,
        чтобы они не были включены в итоговое представление данных для сериализации."""

        data = super().to_representation(instance)
        if data["discount_price"] is None:
            del data["discount_price"]
        if data["discount"] == 0:
            del data["discount"]
        return data


class ProductStaffSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    quantity = serializers.IntegerField()
    discount = serializers.IntegerField()
    available = serializers.BooleanField(default=True)
    cost_price = serializers.DecimalField(max_digits=6, decimal_places=2)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M")

    def validate(self, attrs):
        """
        Проверяет цену товара после применения скидки, чтобы убедиться, что она не опустилась ниже его себестоимости.
        """
        cost_price = Decimal(attrs.get("cost_price", 0))
        price = Decimal(attrs.get("price", 0))
        discount = Decimal(attrs.get("discount", 0))
        loss_factor = Decimal("0.95")

        min_acceptable_price = cost_price * loss_factor
        discounted_price = price * (1 - discount / 100)

        if discounted_price < min_acceptable_price:
            raise serializers.ValidationError(
                "Цена товара после применения скидки не может быть ниже себестоимости."
            )

        return attrs

    def create(self, validated_data):
        validated_data["created_at"] = timezone.now()
        validated_data["updated_at"] = timezone.now()

        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        category = validated_data.get("category", instance.category)

        instance.name = validated_data.get("name", instance.name)
        instance.price = validated_data.get("price", instance.price)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.discount = validated_data.get("discount", instance.discount)
        instance.available = validated_data.get("available", instance.available)
        instance.cost_price = validated_data.get("cost_price", instance.cost_price)
        instance.updated_at = timezone.now()
        if category != instance.category:
            raise serializers.ValidationError("Вы не можете изменить категорию.")
        instance.save()
        return instance


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
