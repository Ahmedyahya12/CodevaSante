from rest_framework.permissions import BasePermission
from authentication.models import UserRole


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRole.RECEPTIONIST, UserRole.ADMIN]
        )