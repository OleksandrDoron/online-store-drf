import django_filters
from django_filters import rest_framework as filters
from store.models import Product


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = CharFilterInFilter(
        field_name="category__name",
        lookup_expr="in",
        label="Category (specify one or more categories, separated by commas)",
    )
    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Minimum Price (filter products with a price higher than or equal to the specified)",
    )
    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Maximum Price (filter products with a price lower than or equal to the specified)",
    )
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Name (enter a part or full name of the product for search)",
    )

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "name"]
