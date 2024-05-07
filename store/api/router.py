from rest_framework import routers

from store.api.views import ProductSearchViewSet, ProductStaffViewSet

router = routers.DefaultRouter()
router.register("product", ProductSearchViewSet, basename="product")
router.register("product_staff", ProductStaffViewSet, basename="product_staff")
