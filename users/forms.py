from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Customer, Worker


class CustomerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "phone_number",
            "location",
        ]


class WorkerRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)
    skillset = forms.CharField(max_length=200)
    per_hour_rate = forms.FloatField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "phone_number",
            "location",
            "skillset",
            "per_hour_rate",
        ]


class CustomerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["phone_number", "location"]


class WorkerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["phone_number", "location", "skillset", "per_hour_rate"]


class WorkerSkillsUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["skillset"]


class WorkerRateUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["per_hour_rate"]
