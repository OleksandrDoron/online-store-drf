from django.urls import path, include

from store.api.router import router
from store.api.views import CategoryList


urlpatterns = [
    path("api/v1/", include(router.urls)),
    path("api/v1/category/", CategoryList.as_view()),
]
