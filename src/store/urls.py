from django.urls import path, include

from store.api.router import router
from store.api.views import (
    ProductCreateAPIView,
    ProductDetailUpdateAPIView,
    CategoryCreateAPIView,
    CategoryDetailAPIView,
    ProductDestroyAPIView,
    CategorySearchAPIView,
)

API_PREFIX = "v1/"

urlpatterns = [
    path(
        API_PREFIX,
        include(
            [
                path("", include(router.urls)),
                path(
                    "products/", ProductCreateAPIView.as_view(), name="product-create"
                ),
                path(
                    "products/<int:pk>/",
                    ProductDetailUpdateAPIView.as_view(),
                    name="product-detail-update-destroy",
                ),
                path(
                    "categories/",
                    CategoryCreateAPIView.as_view(),
                    name="category-create",
                ),
                path(
                    "categories/<int:pk>/",
                    CategoryDetailAPIView.as_view(),
                    name="category-detail-delete",
                ),
                path(
                    "categories/search",
                    CategorySearchAPIView.as_view(),
                    name="category-search",
                ),
            ]
        ),
    )
]
