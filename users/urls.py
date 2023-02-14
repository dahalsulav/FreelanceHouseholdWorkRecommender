from django.urls import path
from users.views import (
    CustomerSignUp,
    CustomerLogin,
    CustomerLogout,
    CustomerProfile,
    CustomerProfileUpdate,
    WorkerSignUp,
    WorkerLogin,
    WorkerLogout,
    WorkerProfile,
    WorkerProfileUpdate,
    WorkerSkillsUpdate,
    WorkerRateUpdate,
)
from django.shortcuts import render

app_name = "users"


def base(request):
    return render(request, "base.html")


urlpatterns = [
    path("", base, name="base"),
    path("customer/signup/", CustomerSignUp.as_view(), name="customer_signup"),
    path("customer/login/", CustomerLogin.as_view(), name="customer_login"),
    path("customer/logout/", CustomerLogout.as_view(), name="customer_logout"),
    path("customer/profile/", CustomerProfile.as_view(), name="customer_profile"),
    path(
        "customer/profile/update/",
        CustomerProfileUpdate.as_view(),
        name="customer_profile_update",
    ),
    path("worker/signup/", WorkerSignUp.as_view(), name="worker_signup"),
    path("worker/login/", WorkerLogin.as_view(), name="worker_login"),
    path("worker/logout/", WorkerLogout.as_view(), name="worker_logout"),
    path("worker/profile/", WorkerProfile.as_view(), name="worker_profile"),
    path(
        "worker/profile/update/",
        WorkerProfileUpdate.as_view(),
        name="worker_profile_update",
    ),
    path(
        "worker/skills/update/",
        WorkerSkillsUpdate.as_view(),
        name="worker_skills_update",
    ),
    path(
        "worker/rate/update/",
        WorkerRateUpdate.as_view(),
        name="worker_rate_update",
    ),
]
