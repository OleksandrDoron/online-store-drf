from decimal import Decimal
from rest_framework import serializers
from config.constants import LOSS_FACTOR


def validate_price(cost_price: Decimal, price: Decimal, discount: int) -> None:
    """
    Validates the product price after applying a discount to ensure it does not fall below its cost price.
    """
    # Calculate the minimum acceptable price after discount
    min_acceptable_price = cost_price * LOSS_FACTOR
    price_after_discount = price * (1 - Decimal(discount) / 100)

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
