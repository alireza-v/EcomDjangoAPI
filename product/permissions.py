from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        """
        Ensure user is a staff member
        """
        return bool(request.user and request.user.is_staff)
