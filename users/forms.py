from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from users.models import Customer, Worker

User = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)


class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "password1",
            "password2",
        ]


class CustomerProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
        ]


class WorkerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)
    skillset = forms.CharField()
    hourly_rate = forms.FloatField()

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "skillset",
            "hourly_rate",
            "password1",
            "password2",
        ]


class WorkerProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)
    skillset = forms.CharField(widget=forms.Textarea)
    hourly_rate = forms.FloatField()

    class Meta:
        model = Worker
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "skillset",
            "hourly_rate",
        ]


class WorkerRateUpdateForm(forms.ModelForm):
    per_hour_rate = forms.FloatField()

    class Meta:
        model = Worker
        fields = ["hourly_rate"]


class WorkerSkillsUpdateForm(forms.ModelForm):
    skillset = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Worker
        fields = ["skillset"]
