from rest_framework import routers

from .views import *

router = routers.DefaultRouter()
router.register(r"product", ProductSearchViewSet, basename="product")
router.register(r"product_staff", ProductStaffViewSet, basename="product_staff")
