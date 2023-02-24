from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission, User
from django.contrib.auth.views import (
    LoginView as Login,
    LogoutView as Logout,
)
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage, BadHeaderError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import (
    FormView,
    TemplateView,
    UpdateView,
)
from users.forms import (
    CustomerProfileUpdateForm,
    CustomerRegistrationForm,
    WorkerProfileUpdateForm,
    WorkerRateUpdateForm,
    WorkerRegistrationForm,
    WorkerSkillsUpdateForm,
    LoginForm,
)
from users.models import Customer, Worker
from users.tokens import account_activation_token
from django.conf import settings


class CustomerSignUp(TemplateView):
    template_name = "signup_customer.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy("registration/account_activation_sent")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # Check if email already exists
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                form.add_error("email", "This email is already registered.")
                return render(request, self.template_name, {"form": form})

            # Check if username already exists
            username = form.cleaned_data.get("username")
            if User.objects.filter(username=username).exists():
                form.add_error("username", "This username is already taken.")
                return render(request, self.template_name, {"form": form})

            # Check if phone number already exists
            phone_number = form.cleaned_data.get("phone_number")
            if Customer.objects.filter(phone_number=phone_number).exists():
                form.add_error(
                    "phone_number", "This phone number is already registered."
                )
                return render(request, self.template_name, {"form": form})

            # Create the user and customer instances
            user = form.save(commit=False)
            user.is_customer = True
            user.is_active = False
            user.email = email
            try:
                user.save()
            except ValidationError as e:
                form.add_error(None, f"An error occurred while creating the user: {e}")
                return render(request, self.template_name, {"form": form})

            customer = Customer.objects.create(
                phone_number=phone_number,
                location=form.cleaned_data["location"],
            )

            # Send email to customer
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string(
                "acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            try:
                email.send()
            except BadHeaderError as e:
                form.add_error(None, "An error occurred while sending the email.")
                return render(request, self.template_name, {"form": form})

            # Send notification email to admin
            admin_email = settings.ADMIN_EMAIL
            message = render_to_string(
                "new_customer_notification.html",
                {
                    "customer": customer,
                },
            )
            email = EmailMessage("New customer sign up", message, to=[admin_email])
            try:
                email.send()
            except BadHeaderError as e:
                form.add_error(None, "An error occurred while sending the email.")
                return render(request, self.template_name, {"form": form})

            return redirect("registration/account_activation_sent")
        else:
            form.add_error(None, "An error occurred while validating the form.")
            return render(request, self.template_name, {"form": form})


class CustomerLogin(Login):
    template_name = "customer_login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            customer = Customer.objects.get(user=user)
            if customer.email_verified:
                login(self.request, user)
                return super().form_valid(form)
            else:
                messages.error(
                    self.request,
                    "Your email is not verified. Please verify your email before logging in.",
                )
                return self.form_invalid(form)
        else:
            messages.error(self.request, "Invalid email or password.")
            return self.form_invalid(form)


class CustomerLogout(LoginRequiredMixin, Logout):
    template_name = "customer_logout.html"
    success_url = reverse_lazy("customer_login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_customer:
            return super().dispatch(request, *args, **kwargs)
        else:
            messages.error(request, "You are not logged in as a customer.")
            return redirect("customer_login")


class CustomerProfile(LoginRequiredMixin, TemplateView):
    template_name = "customer_profile.html"
    login_url = "/customer/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = Customer.objects.get(user=self.request.user)
        return context


class CustomerProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerProfileUpdateForm
    template_name = "customer_profile_update.html"
    success_url = "/customer/profile/"
    login_url = "/customer/login/"

    def get_object(self, queryset=None):
        return Customer.objects.get(user=self.request.user)


class WorkerSignUp(TemplateView):
    template_name = "signup_worker.html"

    def get(self, request, *args, **kwargs):
        form = WorkerRegistrationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_worker = True
            user.is_active = False
            user.refresh_from_db()
            user.email = email
            try:
                user.save()
            except ValidationError as e:
                form.add_error(None, f"An error occurred while creating the user: {e}")
                return render(request, self.template_name, {"form": form})

            worker = Worker.objects.create(
                phone_number=form.cleaned_data.get("phone_number"),
                location=form.cleaned_data.get("location"),
                skillset=form.cleaned_data.get("skills"),
                hourly_rate=form.cleaned_data.get("hourly_rate"),
            )

            # send email to worker
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string(
                "acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            # send notification email to admin
            admin_email = "freelancehhwr@gmail.com"
            message = render_to_string(
                "new_worker_notification.html",
                {
                    "worker": worker,
                },
            )
            email = EmailMessage("New worker sign up", message, to=[admin_email])
            email.send()

            return redirect("registration/account_activation_sent")
        return render(request, self.template_name, {"form": form})


class WorkerLogin(Login):
    template_name = "worker_login.html"
    form_class = LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            worker = Worker.objects.get(user=user)
            if worker.email_verified:
                if worker.approved:
                    login(self.request, user)
                    return super().form_valid(form)
                else:
                    messages.error(
                        self.request,
                        "Your account is pending approval from the admin. Please try again later.",
                    )
                    return self.form_invalid(form)
            else:
                messages.error(
                    self.request,
                    "Your email is not verified. Please verify your email before logging in.",
                )
                return self.form_invalid(form)
        else:
            messages.error(self.request, "Invalid email or password.")
            return self.form_invalid(form)


class WorkerLogout(LoginRequiredMixin, Logout):
    template_name = "worker_logout.html"
    success_url = reverse_lazy("worker_login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("worker_login"))
        return super().dispatch(request, *args, **kwargs)


class WorkerProfile(LoginRequiredMixin, TemplateView):
    template_name = "worker_profile.html"
    login_url = "/login/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["worker"] = Worker.objects.get(user=self.request.user)
        return context


class WorkerProfileUpdate(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = "worker_profile_update.html"
    form_class = WorkerProfileUpdateForm
    success_url = "/worker-profile/"
    login_url = "/worker/login/"

    def get_object(self, queryset=None):
        worker = Worker.objects.filter(user=self.request.user)
        if worker.exists():
            return worker.first()
        else:
            raise PermissionDenied


class WorkerSkillsUpdate(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = "worker_skills_update.html"
    form_class = WorkerSkillsUpdateForm
    success_url = "/worker-profile/"
    login_url = "/worker/login/"

    def get_object(self, queryset=None):
        worker = Worker.objects.filter(user=self.request.user)
        if worker.exists():
            return worker.first()
        else:
            raise PermissionDenied


class WorkerRateUpdate(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = "worker_rate_update.html"
    form_class = WorkerRateUpdateForm
    success_url = "/worker-profile/"
    login_url = "/worker/login/"

    def get_object(self, queryset=None):
        worker = Worker.objects.filter(user=self.request.user)
        if worker.exists():
            return worker.first()
        else:
            raise PermissionDenied
