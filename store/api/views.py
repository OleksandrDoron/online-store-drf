from django.core.exceptions import ObjectDoesNotExist
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
    """
    Search products.
    """
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


class ProductCreateAPIView(APIView):
    """
    Create a new product.
    """
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for creating a new product.",
        request_body=ProductStaffSerializer)
    def post(self, request):
        serializer = ProductStaffSerializer(data=request.data)
        # Check data validity
        if not serializer.is_valid():
            errors_with_message = {
                "message": "Validation error occurred.",
                "errors": serializer.errors,
            }
            return Response(errors_with_message, status=status.HTTP_400_BAD_REQUEST)

        # Check the existence of the specified category
        try:
            Category.objects.get(name=request.data.get('category'))
        except ObjectDoesNotExist:
            return Response(
                {"message": "This category doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the existence of a product with the specified name
        try:
            Product.objects.get(name=request.data.get('name'))
            return Response(
                {"message": "A product with the same name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
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


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View, update, or delete a product.
    """
    serializer_class = ProductStaffSerializer
    queryset = Product.objects.all()
    permission_classes = (IsAdmin, IsAuthenticated)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {"message": "Validation error occurred.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.name = serializer.validated_data.get("name", instance.name)
        instance.price = serializer.validated_data.get("price", instance.price)
        instance.quantity = serializer.validated_data.get(
            "quantity", instance.quantity
        )
        instance.discount = serializer.validated_data.get(
            "discount", instance.discount
        )
        instance.available = serializer.validated_data.get(
            "available", instance.available
        )
        instance.cost_price = serializer.validated_data.get(
            "cost_price", instance.cost_price
        )
        instance.save()
        return Response(
            {"message": "Product successfully updated", "product": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Product removed successfully"},
                        status=status.HTTP_204_NO_CONTENT)


class CategoryCreateAPIView(generics.ListCreateAPIView):
    """
    Create a new category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if not serializer.is_valid():
            errors_with_message = {
                "message": "Validation error occurred.",
                "errors": serializer.errors,
            }
            return Response(errors_with_message, status=status.HTTP_400_BAD_REQUEST)
        try:
            Category.objects.get(name=request.data.get('name'))
            return Response(
                {"message": "A category with the same name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            new_category = Category.objects.create(
                name=request.data.get('name')
            )
        response_data = {
            "message": "Category successfully created",
            "category": CategorySerializer(new_category).data,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveDestroyAPIView):
    """
    View and delete a category.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Category removed successfully"},
                        status=status.HTTP_204_NO_CONTENT)