from django.urls import path
from django.contrib.auth import views as auth_views

from . import views


app_name = "users"

urlpatterns = [
    # Customer registration and login views
    path(
        "register/",
        views.CustomerRegistrationView.as_view(),
        name="customer_registration",
    ),
    path("login/", views.CustomerLoginView.as_view(), name="customer_login"),
    path("logout/", views.CustomerLogoutView.as_view(), name="customer_logout"),
    path(
        "profile/", views.CustomerProfileUpdateView.as_view(), name="customer_profile"
    ),
    # Worker registration and login views
    path(
        "register/worker/",
        views.WorkerRegistrationView.as_view(),
        name="worker_registration",
    ),
    path("login/worker/", views.WorkerLoginView.as_view(), name="worker_login"),
    path("logout/worker/", views.WorkerLogoutView.as_view(), name="worker_logout"),
    path(
        "profile/worker/",
        views.WorkerProfileUpdateView.as_view(),
        name="worker_profile",
    ),
    # Password reset views
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            subject_template_name="users/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
