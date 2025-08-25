import os

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
        title=os.getenv("API_TITLE", "API-title"),
        default_version="v1",
        description=os.getenv("API_DESCRIPTION", "API-description"),
        contact=openapi.Contact(
            email=os.getenv("API_CONTACT_EMAIL", "contact-email@example.com")
        ),
        license=openapi.License(name=os.getenv("API_LICENSE_NAME", "API-license")),
    ),
    public=True,
    generator_class=CustomSchemaGenerator,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    # Landing page being redirected to Swagger
    path("", RedirectView.as_view(url="swagger/"), name="redirection"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # Internal endpoints
    path("api/v1/auth/", include("users.urls")),
    path("api/v1/products/", include("product.urls")),
    path("api/v1/checkout/", include("cart.urls")),
    # Djoser endpoints
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("auth/jwt/logout/", TokenBlacklistView.as_view(), name="jwt_logout"),
]

# Serve uploaded files in DEBUG
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

# Custom 404 Not Found
handler404 = "core.errors.custom_404"
