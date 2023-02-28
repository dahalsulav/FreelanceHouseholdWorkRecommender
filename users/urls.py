from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import messages
from users import views


app_name = "users"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # Customer registration and login views
    path(
        "register/",
        views.CustomerRegistrationView.as_view(),
        name="customer_registration",
    ),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate_account"),
    path(
        "registration/done/",
        views.CustomerRegistrationDoneView.as_view(),
        name="registration_done",
    ),
    path("login/", views.CustomerLoginView.as_view(), name="customer_login"),
    path("logout/", views.CustomerLogoutView.as_view(), name="customer_logout"),
    path(
        "profile/", views.CustomerProfileUpdateView.as_view(), name="customer_profile"
    ),
    # Worker registration and login views
    path(
        "worker/register/",
        views.WorkerRegistrationView.as_view(),
        name="worker_registration",
    ),
    path("worker/login/", views.WorkerLoginView.as_view(), name="worker_login"),
    path("worker/logout/", views.WorkerLogoutView.as_view(), name="worker_logout"),
    path(
        "worker/profile/",
        views.WorkerProfileUpdateView.as_view(),
        name="worker_profile",
    ),
    # Password reset views
    path(
        "password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

# add the message tags for different levels
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "error",
}
