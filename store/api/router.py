from rest_framework import routers

from store.api.views import ProductSearchViewSet

router = routers.DefaultRouter()
router.register("product", ProductSearchViewSet, basename="product")

