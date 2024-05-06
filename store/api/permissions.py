from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name="Клиент").exists()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.groups.filter(name="Администратор").exists()
