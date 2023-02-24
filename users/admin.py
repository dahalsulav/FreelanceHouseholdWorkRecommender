from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Customer, Worker


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
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
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
        ("Customer Info", {"fields": ("is_customer",)}),
    )


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "location",
        "email_verified",
    )


class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "phone_number",
        "location",
        "hourly_rate",
        "is_available",
    )


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Worker, WorkerAdmin)

admin.site.register(User, CustomUserAdmin)
admin.site.unregister(User)
