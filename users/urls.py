from django.urls import path

from . import views

urlpatterns = [
    path(
        "activate/<uid>/<token>/",
        views.activate_user_view,
        name="activation",
    ),
]
