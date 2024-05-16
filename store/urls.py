from django.urls import path, include

from store.api.router import router
from store.api.views import CategoryList, ProductCreateAPIView, ProductUpdateAPIView

urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/product/add", ProductCreateAPIView.as_view(), name="product_add"),
    path("api/v1/products/<int:pk>/", ProductUpdateAPIView.as_view(), name="product-update"),
    path("api/v1/category/<int:pk>/", CategoryList.as_view()),
]
