from typing import Optional
from store import models as app_models


class DiscountPriceMixin:
    @staticmethod
    def get_discounted_price(obj: app_models.Product) -> Optional[float]:
        """
        Calculates the discounted price of a product.
        """
        if obj.discount:
            return obj.price - (obj.price * obj.discount / 100)
        return None

    @staticmethod
    def remove_discount_fields(data: dict[str]) -> Optional[dict]:
        """
        Removes discount-related fields from the data dictionary if they are present.
        """
        if data["discounted_price"] is None:
            data.pop("discounted_price", None)
            data.pop("discount", None)
        return data
