import django_filters
from django_filters import rest_framework as filters
from store.models import Product


class CharFilterInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = CharFilterInFilter(
        field_name="category__name",
        lookup_expr="in",
        label="Категория (укажите одну или несколько категорий, разделяя запятыми)",
    )
    min_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="gte",
        label="Минимальная цена (отфильтровать продукты с ценой выше или равной указанной)",
    )
    max_price = filters.NumberFilter(
        field_name="price",
        lookup_expr="lte",
        label="Максимальная цена (отфильтровать продукты с ценой ниже или равной указанной)",
    )
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Название (введите часть или полное название продукта для поиска)",
    )

    class Meta:
        model = Product
        fields = ["category", "min_price", "max_price", "name"]
