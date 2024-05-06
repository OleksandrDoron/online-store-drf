from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register("product", ProductSearchViewSet, basename="product")
router.register("product_staff", ProductStaffViewSet, basename="product_staff")
