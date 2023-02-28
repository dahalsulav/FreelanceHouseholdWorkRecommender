from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from users.models import Customer


class CustomerAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_customer",
        "email_verified",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_customer", "email_verified")
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "location",
                )
            },
        ),
        (
            _("Permissions"),
            {"fields": ("is_customer", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone_number",
                    "location",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    ordering = ("email",)
    actions = ["delete_model"]

    def delete_model(self, request, obj):
        """
        Deletes a customer account and sends a confirmation message.
        """
        obj.email_user(
            "Account Deletion Notification", "Your account has been deleted."
        )
        obj.delete()
        self.message_user(request, "The customer account has been deleted.")

    delete_model.short_description = "Delete selected customers"


admin.site.register(Customer, CustomerAdmin)
