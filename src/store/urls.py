from django.urls import path, include

from store.api.router import router
from store.api.views import (
    ProductCreateAPIView,
    ProductUpdateAPIView,
    CategoryCreateAPIView,
    CategoryDetailAPIView, ProductDestroyAPIView, CategorySearchAPIView,
)

urlpatterns = [
    # product endpoints
    path("api/v1/", include(router.urls)),
    path("api/v1/products/create", ProductCreateAPIView.as_view(), name="product-create"),
    path("api/v1/products/<int:pk>/", ProductUpdateAPIView.as_view(), name="product-detail"),
    path("api/v1/product/delete/<int:pk>/", ProductDestroyAPIView.as_view(), name="product-destroy"),

    # category endpoints
    path("api/v1/categories/create", CategoryCreateAPIView.as_view(), name="category-create"),
    path("api/v1/categories/<int:pk>/", CategoryDetailAPIView.as_view(), name="category-detail-delete"),
    path("api/v1/categories/", CategorySearchAPIView.as_view(), name="category-search"),

]
