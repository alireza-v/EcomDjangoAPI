from django.http import JsonResponse
from rest_framework import status


def custom_404(request, exception):
    return JsonResponse(
        {
            "detail": "Page not found",
        },
        status=status.HTTP_404_NOT_FOUND,
    )
