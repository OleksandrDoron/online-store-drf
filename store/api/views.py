from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from store.api.filters import ProductFilter
from store.api.permissions import IsAdmin
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
    permission_classes = (IsAdmin, IsAuthenticated)
    """
    API endpoint for creating a new product.
    """

    def post(self, request):
        serializer = ProductStaffSerializer(data=request.data)
        # Check data validity
        if serializer.is_valid():

            # Check if a product with the same name already exists
            if Product.objects.filter(name=request.data.get("name")).exists():
                return Response({"message": "Product with this name already exists."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check if the specified category exists
            if not Category.objects.filter(name=request.data.get("category")).exists():
                return Response({"message": f"Category does not exist."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Create a new product
            new_product = Product.objects.create(
                name=request.data.get("name"),
                category=Category.objects.get(name=request.data.get("category")),
                price=request.data.get("price"),
                quantity=request.data.get("quantity"),
                discount=request.data.get("discount"),
                available=request.data.get("available", True),
                cost_price=request.data.get("cost_price"),
            )
            # Return response with created product data and success message
            response_data = {
                "message": "Product successfully created",
                "product": ProductStaffSerializer(new_product).data,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        else:
            # Return response with validation error message
            errors_with_message = {
                "message": "Validation error occurred.",
                "errors": serializer.errors,
            }
            return Response(errors_with_message, status=status.HTTP_400_BAD_REQUEST)


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
