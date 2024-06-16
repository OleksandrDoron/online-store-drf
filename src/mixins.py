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
