from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from store.api.filters import ProductFilter
from store.models import Product, Category
from store.api.serializers import (
    CategorySerializer,
    ProductStaffSerializer,
    ProductSerializer,
)


class ProductSearchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    CATEGORY = openapi.Parameter(
        name="category",
        in_=openapi.IN_QUERY,
        description="Filter products by category. Use commas to specify multiple categories.",
        type=openapi.TYPE_STRING,
    )
    MIN_PRICE = openapi.Parameter(
        name="min_price",
        in_=openapi.IN_QUERY,
        description="Filter products by minimum price.",
        type=openapi.TYPE_NUMBER,
    )
    MAX_PRICE = openapi.Parameter(
        name="max_price",
        in_=openapi.IN_QUERY,
        description="Filter products by maximum price.",
        type=openapi.TYPE_NUMBER,
    )
    NAME = openapi.Parameter(
        name="name",
        in_=openapi.IN_QUERY,
        description="Filter products by name. Search is case-insensitive.",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[CATEGORY, MIN_PRICE, MAX_PRICE, NAME])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductStuffViewSet(viewsets.ModelViewSet):
    serializer_class = ProductStaffSerializer
    queryset = Product.objects.all()


class ProductCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ProductStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_product = Product.objects.create(
            name=request.data.get('name'),
            category=Category.objects.get(name=request.data.get('category')),
            price=request.data.get('price'),
            quantity=request.data.get('quantity'),
            discount=request.data.get('discount'),
            available=request.data.get('available', True),
            cost_price=request.data.get('cost_price'),
        )

        return Response({'post': ProductStaffSerializer(new_product).data})


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
