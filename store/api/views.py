from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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


class ProductCreateAPIView(generics.CreateAPIView):
    """
    Create a new product.
    """

    serializer_class = ProductStaffSerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for creating a new product.",
        request_body=ProductStaffSerializer,
        responses={201: openapi.Response("Product", ProductStaffSerializer)},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # Check data validity
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check the existence of the specified category
        try:
            category = Category.objects.get(name=request.data.get("category"))
        except ObjectDoesNotExist:
            return Response(
                {"message": "This category doesn't exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the existence of a product with the specified name
        try:
            Product.objects.get(name=request.data.get("name"))
            return Response(
                {"message": "A product with the same name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            new_product = Product.objects.create(
                name=serializer.validated_data.get("name"),
                category=category,
                price=serializer.validated_data.get("price"),
                quantity=serializer.validated_data.get("quantity"),
                discount=serializer.validated_data.get("discount"),
                available=serializer.validated_data.get("available"),
                cost_price=serializer.validated_data.get("cost_price"),
            )
            return Response(
                ProductStaffSerializer(new_product).data, status=status.HTTP_201_CREATED
            )


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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update the object fields based on the serializer data
        for attr, value in serializer.validated_data.items():
            if attr == "category":
                try:
                    category = Category.objects.get(name=request.data.get("category"))
                    setattr(instance, attr, category)
                except ObjectDoesNotExist:
                    return Response(
                        {"error": "Category does not exist."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                setattr(instance, attr, value)
        instance.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryCreateAPIView(generics.ListCreateAPIView):
    """
    Create a new category.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            Category.objects.get(name=request.data.get("name"))
            return Response(
                {"message": "A category with the same name already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            new_category = Category.objects.create(name=request.data.get("name"))
        return Response(
            CategorySerializer(new_category).data, status=status.HTTP_201_CREATED
        )


class CategoryDetailView(generics.RetrieveDestroyAPIView):
    """
    View and delete a category.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)
