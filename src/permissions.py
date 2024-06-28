from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_admin:
            return True
        return False


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_client
