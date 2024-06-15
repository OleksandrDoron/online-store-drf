from django.core.exceptions import ObjectDoesNotExist
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from store.api.filters import ProductFilter
from store.api.permissions import IsAdmin
from store.models import Product, Category
from store.api.serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer, ProductSearchSerializer,
    ProductPartialUpdateSerializer,
)


class ProductSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A view set for searching products.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSearchSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter

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
                "List of products.", ProductSearchSerializer(many=True)
            )
        },
        operation_id="ListProducts",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="API endpoint for retrieving a product by ID.",
        responses={200: openapi.Response("Product details.", ProductSearchSerializer)},
        operation_id="RetrieveProductByID",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


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
            category = Category.objects.get(name=serializer.validated_data["category"])
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


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    A view for viewing, updating, or deleting a product.
    """

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = (IsAdmin, IsAuthenticated)

    @swagger_auto_schema(
        operation_description="API endpoint for retrieving a product by ID.",
        responses={200: openapi.Response("Product details.", ProductSerializer)},
        operation_id="RetrieveProductByIDStaff",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @staticmethod
    def _update_product_swagger_auto_schema(method):
        """
        Static method for documenting the put and patch methods.
        """
        return swagger_auto_schema(
            operation_description="API endpoint for updating a product by ID.",
            request_body=ProductSerializer,
            responses={200: openapi.Response("Product updated.", ProductSerializer)},
            operation_id="UpdateProductByIDStaff",
        )(method)

    @_update_product_swagger_auto_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @_update_product_swagger_auto_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update the object fields based on the serializer data
        for attr, value in serializer.validated_data.items():
            if attr == "category":
                try:
                    category = Category.objects.get(
                        name=serializer.validated_data["category"]
                    )
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

    @swagger_auto_schema(
        operation_description="API endpoint for deleting a product by ID.",
        operation_id="DeleteProductByIDStaff",
        responses={204: openapi.Response(description="Product deleted successfully.")},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


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


class CategoryDetailView(generics.RetrieveDestroyAPIView):
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
