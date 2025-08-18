from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenBlacklistView

from .swagger import CustomSchemaGenerator

schema_view = get_schema_view(
    openapi.Info(
        title="Ecommerce API",
        default_version="v1",
        description="API documentation for the project.",
        contact=openapi.Contact(email="alirezasonym5@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    generator_class=CustomSchemaGenerator,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="swagger/"), name="redirection"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # apps
    path("api/users/", include("users.urls")),
    path("api/products/", include("product.urls")),
    path("api/checkout/", include("cart.urls")),
    # Djoser
    re_path(r"^auth/", include("djoser.urls")),
    re_path(r"^auth/", include("djoser.urls.jwt")),
    path("auth/jwt/logout/", TokenBlacklistView.as_view(), name="jwt_logout"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler404 = "product.views.custom_404_view"
