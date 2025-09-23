from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from dotenv import load_dotenv
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenBlacklistView

from core.swagger import CustomSchemaGenerator

load_dotenv()

schema_view = get_schema_view(
    openapi.Info(
        title="CortexCommerce",
        default_version="v1",
        license=openapi.License(name="BSD License"),
        description="""
    This API allows users to:
    - Browse products and categories
    - Manage shopping carts and orders
    - Apply discounts and process payments
    - Track order history and feedback
    All endpoints are secured where necessary and return JSON responses.
    For authentication, use JWT tokens
    """,
    ),
    public=True,
    generator_class=CustomSchemaGenerator,
)


urlpatterns = (
    [
        path("admin/", admin.site.urls),
        # Redirection
        path("", RedirectView.as_view(url="swagger/"), name="redirection"),
        path(
            "swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"
        ),
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        # Internal endpoints
        path("api/v1/auth/", include("users.urls")),
        path("api/v1/products/", include("product.urls")),
        path("api/v1/carts/", include("cart.urls")),
        path("api/v1/checkout/", include("orders.urls")),
        path("api/v1/payments/", include("payments.urls")),
        # Djoser endpoints
        re_path(r"^auth/", include("djoser.urls")),
        re_path(r"^auth/", include("djoser.urls.jwt")),
        path("auth/jwt/logout/", TokenBlacklistView.as_view(), name="jwt_logout"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

# Serve uploaded files in DEBUG
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# Custom 404 Not Found
handler404 = "core.errors.custom_404"
