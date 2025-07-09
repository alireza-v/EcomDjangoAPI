from rest_framework import status
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, Throttled):
        return Response(
            {
                "message": "Too many requests. Please try again later.",
                "available_in_seconds": exc.wait,
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return response


# del
