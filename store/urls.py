from django.urls import path, include

from store.api.router import router
from store.api.views import ProductCreateAPIView, ProductDetailAPIView, CategoryCreateAPIView, CategoryDetailView

urlpatterns = [
    # product endpoints
    path("api/v1/", include(router.urls)),
    path("api/v1/product/create", ProductCreateAPIView.as_view(), name="product-create"),
    path("api/v1/product/<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),

    # category endpoints
    path('api/v1/category/', CategoryCreateAPIView.as_view(), name='category-list-create'),
    path('api/v1/category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail-delete'),
]
