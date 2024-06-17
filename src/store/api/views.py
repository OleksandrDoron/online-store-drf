from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.constants import LOSS_FACTOR
from store.api.filters import ProductFilter
from store.api.permissions import IsAdmin
from store.models import Product, Category
from store.api.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductSearchSerializer,
    ProductPartialUpdateSerializer,
)


class ProductSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for searching products.
    """

    queryset = Product.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

    # Select serializer based on the action
    def get_serializer_class(self):
        action_serializers_dict = {
            "list": ProductSearchSerializer,
            "retrieve": ProductDetailSerializer,
        }
        serializer = action_serializers_dict.get(self.action)
        if not serializer:
            raise Exception(f"Serializer for {self.action=} is not exist")
        return serializer

    # Parameters for filtering products
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

    @swagger_auto_schema(
        operation_description="API endpoint for listing products with optional filters.",
        manual_parameters=[CATEGORY, MIN_PRICE, MAX_PRICE, NAME],
        responses={
            200: openapi.Response(
                "List of products.", ProductDetailSerializer(many=True)
            )
        },
        operation_id="ListProducts",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="API endpoint for retrieving a product by ID.",
        responses={200: openapi.Response("Product details.", ProductDetailSerializer)},
        operation_id="RetrieveProductByID",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class CategorySearchAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(
        operation_description="API endpoint for listing categories.",
        responses={200: openapi.Response("List of categories", CategorySerializer)},
        operation_id="ListCategories",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductCreateAPIView(generics.GenericAPIView):
    """
    A view for creating a new product.
    """

    serializer_class = ProductSerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for creating a new product.",
        request_body=ProductSerializer,
        responses={201: openapi.Response("Product created.", ProductSerializer)},
        operation_id="CreateProduct",
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        # Check data validity
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Check the existence of the specified category
        try:
            category = Category.objects.get(id=serializer.validated_data["category_id"])
        except ObjectDoesNotExist:
            return Response(
                {"message": "This category doesn't exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check the existence of a product with the specified name
        if Product.objects.filter(name=serializer.validated_data["name"]).exists():
            return Response(
                {"message": "A product with the same name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        product = Product.objects.create(
            name=serializer.validated_data["name"],
            category=category,
            price=serializer.validated_data["price"],
            quantity=serializer.validated_data["quantity"],
            discount=serializer.validated_data["discount"],
            available=serializer.validated_data["available"],
            cost_price=serializer.validated_data["cost_price"],
        )
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)


class ProductUpdateAPIView(generics.GenericAPIView):
    """
    A view for updating a product.
    """

    queryset = Product.objects.all()
    permission_classes = (IsAdmin, IsAuthenticated)

    def get_serializer_class(self):
        action_serializers_dict = {
            "PUT": ProductSerializer,
            "PATCH": ProductPartialUpdateSerializer,
            "GET": ProductSerializer,
        }
        serializer_class = action_serializers_dict.get(self.request.method)
        return serializer_class

    @swagger_auto_schema(
        operation_description="API endpoint for retrieving a product by ID.",
        responses={200: openapi.Response("Product details.", ProductSerializer)},
        operation_id="RetrieveProductByIDStaff",
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="API endpoint for updating a product by ID.",
        responses={200: openapi.Response("Product updated.", ProductSerializer)},
        operation_id="UpdateProduct",
    )
    def put(self, request, *args, **kwargs):
        return self.update_product(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="API endpoint for partially updating a product by ID.",
        responses={200: openapi.Response("Product updated.", ProductSerializer)},
        operation_id="PartialUpdateProduct",
    )
    def patch(self, request, *args, **kwargs):
        return self.update_product(request, *args, **kwargs, partial=True)

    def update_product(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop("partial", False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve or use existing values from the instance if none are provided,
        # and check the values before saving (only for partial updates).
        if partial:
            cost_price = serializer.validated_data.get(
                "cost_price", instance.cost_price
            )
            price = serializer.validated_data.get("price", instance.price)
            discount = Decimal(
                serializer.validated_data.get("discount", instance.discount)
            )

            # Calculate the minimum acceptable price after discount
            min_acceptable_price = cost_price * LOSS_FACTOR
            price_after_discount = price * (1 - discount / 100)

            # Check if the price is below the cost price
            if price < cost_price:
                return Response(
                    {"error": "Product price cannot be lower than the cost price."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the discounted price falls below the cost price
            if price_after_discount < min_acceptable_price:
                return Response(
                    {
                        "error": "Product price after applying discount cannot be lower than the cost price."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Update the object fields based on the serializer data
        for attr, value in serializer.validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return Response(ProductSerializer(instance).data, status=status.HTTP_200_OK)


class ProductDestroyAPIView(generics.DestroyAPIView):
    """
    A view for deleting a product.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for deleting a product by ID.",
        operation_id="DeleteProductByIDStaff",
        responses={204: openapi.Response(description="Product deleted successfully.")},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CategoryCreateAPIView(generics.GenericAPIView):
    """
    A view for creating a new category.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for creating a new category.",
        operation_id="CreateCategory",
        request_body=CategorySerializer,
        responses={201: openapi.Response("Category.", CategorySerializer)},
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        category_name = serializer.validated_data["name"]
        try:
            Category.objects.get(name=category_name)
            return Response(
                {"message": "A category with the same name already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ObjectDoesNotExist:
            category = Category.objects.create(name=category_name)
            return Response(
                CategorySerializer(category).data, status=status.HTTP_201_CREATED
            )


class CategoryDetailAPIView(generics.RetrieveDestroyAPIView):
    """
    A view for retrieving or deleting a category by ID.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for retrieving a category by ID.",
        responses={200: openapi.Response("Category details.", ProductSerializer)},
        operation_id="RetrieveProductByIDStaff",
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="API endpoint for deleting a category by ID.",
        operation_id="DeleteCategoryByIDStaff",
        responses={204: openapi.Response(description="Category deleted successfully.")},
    )
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
