from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Show role on the edit user page
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

    # Show role on the add user page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )

    list_display = ("username", "email", "role", "is_staff", "is_superuser")



admin.site.unregister(Group)