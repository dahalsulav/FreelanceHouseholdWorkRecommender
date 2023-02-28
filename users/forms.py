from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.urls import reverse_lazy
from .models import Customer, Worker
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Customer
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "phone_number",
            "location",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if Customer.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("Phone number already exists.")
        return phone_number

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        cleaned_data["password"] = password
        cleaned_data["confirm_password"] = confirm_password

        return cleaned_data


class WorkerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Worker
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password",
            "phone_number",
            "location",
            "skills",
            "hourly_rate",
        ]

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_worker = True
        user.is_active = False
        user.save()
        worker = Worker.objects.create(
            user=user,
            phone_number=self.cleaned_data["phone_number"],
            location=self.cleaned_data["location"],
            skills=self.cleaned_data["skills"],
            hourly_rate=self.cleaned_data["hourly_rate"],
        )
        send_mail(
            subject="Verify your email",
            message="Please click the link below to verify your email.",
            from_email="noreply@freelancehouseholdwork.com",
            recipient_list=[user.email],
            fail_silently=False,
        )
        send_mail(
            subject="New worker registration",
            message="A new worker has registered on Freelance Household Work. Please log in to the admin panel to approve or reject the registration request.",
            from_email="noreply@freelancehouseholdwork.com",
            recipient_list=["admin@freelancehouseholdwork.com"],
            fail_silently=False,
        )
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"autofocus": True, "class": "form-control"})
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control"}
        ),
    )

    error_messages = {
        "invalid_login": "Please enter a correct email and password. Note that both fields may be case-sensitive.",
        "inactive": "This account is inactive.",
    }


class CustomerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "email", "phone_number", "location"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["readonly"] = True


class WorkerProfileUpdateForm(forms.ModelForm):
    """
    A form for updating a worker's profile.

    Allows the worker to update their profile details, such as their name, email,
    phone number, and location. If the worker updates their hourly pay rate, their
    is_active flag will be set to False and the update will require admin approval.
    """

    class Meta:
        model = Worker
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "skills",
            "hourly_rate",
        ]

    def clean_hourly_rate(self):
        """
        If the worker is updating their hourly pay rate, their is_active flag will be
        set to False and the update will require admin approval.

        Returns:
        - Decimal: The validated hourly rate.
        """
        hourly_rate = self.cleaned_data.get("hourly_rate")
        if hourly_rate != self.instance.hourly_rate:
            self.instance.is_active = False
        return hourly_rate
