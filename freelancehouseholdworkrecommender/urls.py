"""
freelancehouseholdworkrecommender URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib import messages

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
]
