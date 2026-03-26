from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ProducerProfile, CustomerProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")

admin.site.register(ProducerProfile)
admin.site.register(CustomerProfile)
