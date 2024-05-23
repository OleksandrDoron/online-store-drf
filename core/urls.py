from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(
        title="Online Store api",
        default_version="v1",
        description="API for an online store. Allows retrieving information about products,"
        "categories, placing orders, and much more.",
    ),
    public=True,
    permission_classes=[AllowAny],
)

swagger_urlpatterns = [
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("store.urls")),
    # auth
    path("api/auth/", include("rest_framework.urls")),
    path("auth/", include("djoser.urls")),
    path(r"auth/", include("djoser.urls.authtoken")),
]

urlpatterns += swagger_urlpatterns
