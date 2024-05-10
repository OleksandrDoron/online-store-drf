from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_admin


class IsClient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_client
