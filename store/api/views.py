from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import ProductFilter
from .permissions import IsAdmin
from store.models import Product, Category
from .serializers import CategorySerializer, ProductStaffSerializer, ProductSerializer


class ProductSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    CATEGORY = openapi.Parameter(
        name="category",
        in_=openapi.IN_QUERY,
        description="Фильтровать продукты по категории. Используйте запятые для указания нескольких категорий.",
        type=openapi.TYPE_STRING,
    )
    MIN_PRICE = openapi.Parameter(
        name="min_price",
        in_=openapi.IN_QUERY,
        description="Фильтровать продукты по минимальной цене.",
        type=openapi.TYPE_NUMBER,
    )
    MAX_PRICE = openapi.Parameter(
        name="max_price",
        in_=openapi.IN_QUERY,
        description="Фильтровать продукты по максимальной цене.",
        type=openapi.TYPE_NUMBER,
    )
    NAME = openapi.Parameter(
        name="name",
        in_=openapi.IN_QUERY,
        description="Фильтровать продукты по названию. Поиск не чувствителен к регистру.",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[CATEGORY, MIN_PRICE, MAX_PRICE, NAME])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductStaffViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductStaffSerializer
    permission_classes = (IsAdmin, IsAuthenticated)


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
