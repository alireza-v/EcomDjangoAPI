from django.urls import path

from .views import activate_user_view, password_change_confirm

urlpatterns = [
    path("auth/activate/<uid>/<token>/", activate_user_view, name="activation"),
    path(
        "auth/password/confirm/<uid>/<token>/",
        password_change_confirm,
        name="password_rest_confirm",
    ),
]
