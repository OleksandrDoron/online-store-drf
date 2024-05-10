from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


class CustomUserAdmin(BaseUserAdmin):
    list_display = ("id", "username", "email", "role", "balance", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        fieldsets += (("Custom Fields", {"fields": ("role",)}),)
        return fieldsets


admin.site.register(User, CustomUserAdmin)
