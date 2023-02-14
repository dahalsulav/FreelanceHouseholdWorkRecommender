from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Worker


class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_customer",
        "is_worker",
        "is_staff",
    )
    list_filter = ("is_customer", "is_worker", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("User type", {"fields": ("is_customer", "is_worker", "is_admin")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "is_customer",
                    "is_worker",
                    "is_admin",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Customer)
admin.site.register(Worker)
