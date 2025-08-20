from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """whether the user is a staff or not"""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_staff,
        )
