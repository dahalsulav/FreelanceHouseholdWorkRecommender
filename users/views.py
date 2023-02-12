from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from django.views.generic import TemplateView
from .forms import CustomerSignUpForm, WorkerSignUpForm
from .models import Customer, Worker
from .tokens import account_activation_token


class CustomerSignUpView(generic.CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = "registration/signup.html"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = "Activate your account."
        message = render_to_string(
            "registration/acc_active_email.html",
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
        return redirect("account_activation_sent")


class CustomerActivateView(TemplateView):
    template_name = "registration/account_activation_sent.html"


class Activate(TemplateView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.customer.is_verified = True
            user.save()
            login(request, user)
            return redirect("home")
        else:
            return render(request, "registration/account_activation_invalid.html")


class WorkerSignUpView(generic.CreateView):
    model = User
    form_class = WorkerSignUpForm
    template_name = "registration/worker_signup.html"

    def form_valid(self, form):
        user = form.save()
        worker = Worker.objects.create(
            user=user,
            phone_number=form.cleaned_data["phone_number"],
            location=form.cleaned_data["location"],
            skillset=form.cleaned_data["skillset"],
            per_hour_rate=form.cleaned_data["per_hour_rate"],
        )
        worker.save()
        current_site = get_current_site(self.request)
        subject = "Activate Your Account"
        message = render_to_string(
            "registration/worker_email_confirmation.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject, message)
        return redirect("registration:worker_email_confirmation_sent")


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = "registration/login.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            login(self.request, user)
            return redirect("home")
        else:
            return render(
                self.request,
                "registration/login.html",
                {"form": form, "error_message": "Invalid login credentials"},
            )


class LogoutView(LoginRequiredMixin, generic.RedirectView):
    url = reverse_lazy("home")

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class EditProfileView(LoginRequiredMixin, generic.UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "registration/edit_profile.html"
    success_url = reverse_lazy("view_profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        if hasattr(user, "customer"):
            user.customer.phone_number = form.cleaned_data["phone_number"]
            user.customer.location = form.cleaned_data["location"]
            user.customer.save()
        elif hasattr(user, "worker"):
            user.worker.phone_number = form.cleaned_data["phone_number"]
            user.worker.location = form.cleaned_data["location"]
            user.worker.save()
        return redirect("view_profile")


class WorkerUpdateProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    template_name = "worker/update_profile.html"
    form_class = WorkerProfileUpdateForm
    success_url = reverse_lazy("worker:view_profile")

    def get_object(self, queryset=None):
        return self.request.user.worker

    def form_valid(self, form):
        form.instance.is_verified = False
        return super().form_valid(form)


class WorkerLoginView(FormView):
    template_name = "worker/login.html"
    form_class = WorkerAuthenticationForm
    success_url = reverse_lazy("worker:view_profile")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(self.request, username=email, password=password)

        if user is not None and user.is_active and user.worker.is_verified:
            login(self.request, user)
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class WorkerViewProfileView(LoginRequiredMixin, TemplateView):
    template_name = "worker/view_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["worker"] = self.request.user.worker
        return context
