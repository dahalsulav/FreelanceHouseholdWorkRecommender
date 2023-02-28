from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.db.models import Avg
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (
    CreateView,
    DetailView,
    FormView,
    TemplateView,
    UpdateView,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from .forms import (
    CustomerProfileUpdateForm,
    CustomerRegistrationForm,
    LoginForm,
    WorkerProfileUpdateForm,
    WorkerRegistrationForm,
)
from .models import Customer, Worker
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class HomeView(TemplateView):
    template_name = "users/base.html"


class CustomerRegistrationView(CreateView):
    """
    A view for customer registration.

    On successful registration, sends email to customer and notification email to admin.

    """

    model = Customer
    form_class = CustomerRegistrationForm
    template_name = "users/registration_form.html"
    success_url = reverse_lazy("users:registration_done")

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        If form is valid, create a new customer and save to the database.

        If email, username, or phone number already exists, redirect back to registration form.

        """
        try:
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            phone_number = form.cleaned_data["phone_number"]

            if User.objects.filter(email=email).exists():
                form.add_error("email", "Email already exists.")
                return self.form_invalid(form)

            if User.objects.filter(username=username).exists():
                form.add_error("username", "Username already exists.")
                return self.form_invalid(form)

            if Customer.objects.filter(phone_number=phone_number).exists():
                form.add_error("phone_number", "Phone number already exists.")
                return self.form_invalid(form)

            # Save customer to the database
            customer = form.save(commit=False)
            customer.is_customer = True
            customer.save()

            # Generate unique token for the customer
            uidb64 = urlsafe_base64_encode(force_bytes(customer.pk))
            token = default_token_generator.make_token(customer)

            # Construct the activation link
            activation_link = f"{self.request.scheme}://{self.request.get_host()}/users/activate/{uidb64}/{token}"

            # Send verification email to customer with activation link
            send_mail(
                subject="Verify your email",
                message=f"Please click the link below to verify your email: {activation_link}",
                from_email=settings.ADMIN_EMAIL,
                recipient_list=[customer.email],
                fail_silently=False,
            )

            # Send notification email to admin
            send_mail(
                subject="New customer registration",
                message="A new customer has registered on Freelance Household Work.",
                from_email=settings.ADMIN_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=False,
            )

            # Success message
            messages.success(
                self.request, "Your account has been created successfully!"
            )

            return super().form_valid(form)

        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class CustomerRegistrationDoneView(TemplateView):
    """
    A view to display a success message after customer registration is complete.
    """

    template_name = "users/registration_done.html"


def activate_account(request, uidb64, token):
    """
    Activate a customer account using the given uidb64 and token.

    If account is already active, redirect to login page with message.

    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        customer = get_object_or_404(Customer, pk=uid)
    except (TypeError, ValueError, OverflowError, Customer.DoesNotExist):
        customer = None

    if customer is not None and default_token_generator.check_token(customer, token):
        if not customer.email_verified:
            # activate the customer account
            customer.email_verified = True  # Set email_verified to True
            customer.save()
            messages.success(request, "Your account has been activated successfully!")
        else:
            messages.info(request, "Your account is already active.")
        return redirect("users:customer_login")
    else:
        messages.error(request, "Invalid activation link.")
        return redirect("users:base")


class CustomerLoginView(FormView):
    """
    A view for logging in a customer.

    Allows the customer to log in to their account.

    Parameters:
    - FormView (class): Django generic view for rendering a form.
    """

    template_name = "users/customer_login.html"
    form_class = LoginForm
    success_url = reverse_lazy("customer_profile")

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Logs the user in and sends a message to confirm the action.

        Parameters:
        - form (LoginForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)

        if isinstance(user, Customer) and user.email_verified:
            login(self.request, user)
            messages.success(self.request, f"You are now logged in as {user.username}.")
            return super().form_valid(form)
        elif isinstance(user, Customer) and not user.email_verified:
            messages.error(
                self.request,
                "Your email address is not verified yet. Please check your email for a verification link.",
            )
            return redirect("users:customer_login")
        else:
            messages.error(self.request, "Invalid email or password.")
            return redirect("users:customer_login")

    def form_invalid(self, form):
        """
        Called when an invalid form is submitted.

        Sends an error message to the user.

        Parameters:
        - form (LoginForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the login URL with an error message.
        """

        messages.error(self.request, "Invalid email or password.")
        return redirect("users:customer_login")


@method_decorator(login_required(login_url="users:customer_login"), name="dispatch")
class CustomerLogoutView(LogoutView):
    """
    A view for logging out a customer.

    Allows the customer to log out of their account.

    Parameters:
    - LogoutView (class): Django generic view for logging a user out.
    """

    next_page = reverse_lazy("users:base")

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the view.

        Logs the customer out and sends a message to confirm the action.

        Parameters:
        - request (HttpRequest): The HTTP request.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - HttpResponse: A redirect to the next page URL with a success message.
        """
        messages.success(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required(login_url="login"), name="dispatch")
class CustomerProfileUpdateView(UpdateView):
    """
    A view for updating a customer's profile.

    Allows the customer to update their profile details, such as their name, email,
    phone number, and location.

    Parameters:
    - UpdateView (class): Django generic view for updating objects in the database.
    """

    model = Customer
    form_class = CustomerProfileUpdateForm
    template_name = "users/customer_profile_update.html"
    success_url = reverse_lazy("customer_profile")

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Saves the form and sends a message to the user to confirm the profile update.

        Parameters:
        - form (CustomerProfileUpdateForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        response = super().form_valid(form)
        self.object.email_verified = False
        self.object.save()
        messages.success(self.request, "Profile updated successfully.")
        return response

    def get_object(self):
        """
        Gets the object being updated.

        Returns:
        - object (Customer): The customer object being updated.
        """
        return Customer.objects.get(user=self.request.user)


class WorkerRegistrationView(CreateView):
    """
    A view for worker registration.

    On successful registration, sends email to worker and notification email to admin.

    """

    model = Worker
    form_class = WorkerRegistrationForm
    template_name = "users/worker_registration_form.html"
    success_url = reverse_lazy("users:account_activation_sent")

    def form_valid(self, form):
        """
        If form is valid, create a new worker and save to the database.

        If email or username already exists, redirect back to registration form.

        """
        try:
            # Check if email already exists
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exists():
                form.add_error("email", "Email already exists.")
                return self.form_invalid(form)

            # Check if username already exists
            username = form.cleaned_data["username"]
            if User.objects.filter(username=username).exists():
                form.add_error("username", "Username already exists.")
                return self.form_invalid(form)

            # Save worker to the database
            user = form.save(commit=False)
            user.is_worker = True
            user.is_active = False  # Worker is inactive until admin approves them
            user.save()

            # Create Worker model instance
            worker = Worker.objects.create(
                user=user,
                phone_number=form.cleaned_data.get("phone_number"),
                location=form.cleaned_data.get("location"),
                skillset=form.cleaned_data.get("skills"),
                hourly_rate=form.cleaned_data.get("hourly_rate"),
            )

            # Send verification email to worker
            send_mail(
                subject="Verify your email",
                message="Please click the link below to verify your email.",
                from_email="noreply@freelancehouseholdwork.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            # Send notification email to admin
            send_mail(
                subject="New worker registration",
                message="A new worker has registered on Freelance Household Work. Please log in to the admin panel to approve or reject the registration request.",
                from_email="noreply@freelancehouseholdwork.com",
                recipient_list=["admin@freelancehouseholdwork.com"],
                fail_silently=False,
            )

            return super().form_valid(form)

        except Exception as e:
            # If an error occurs, show the registration form again
            form.add_error(None, str(e))
            return self.form_invalid(form)


def account_activation_sent(request):
    return render(request, "users/account_activation_sent.html")


class WorkerLoginView(FormView):
    """
    A view for logging in a worker.

    Allows the worker to log in to their account.

    Parameters:
    - FormView (class): Django generic view for rendering a form.
    """

    template_name = "users/worker_login.html"
    form_class = LoginForm
    success_url = reverse_lazy("worker_profile")

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Logs the user in and sends a message to confirm the action.

        Parameters:
        - form (LoginForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, email=email, password=password)

        if user and user.is_worker:
            if not user.email_verified:
                messages.error(
                    self.request,
                    "Your email address has not been verified. Please check your email and follow the verification link.",
                )
                return self.form_invalid(form)

            if not user.is_active:
                messages.error(
                    self.request,
                    "Your account has not been approved by the administrator. Please wait for approval and try again later.",
                )
                return self.form_invalid(form)

            login(self.request, user)
            messages.success(self.request, f"You are now logged in as {user.username}.")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid email or password.")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        Called when an invalid form is submitted.

        Sends an error message to the user.

        Parameters:
        - form (LoginForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the login URL with an error message.
        """
        messages.error(self.request, "Invalid email or password.")
        return super().form_invalid(form)


@method_decorator(login_required(login_url="worker_login"), name="dispatch")
class WorkerLogoutView(LogoutView):
    """
    A view for logging out a worker.

    Allows the worker to log out of their account.

    Parameters:
    - LogoutView (class): Django generic view for logging a user out.
    """

    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the view.

        Logs the worker out and sends a message to confirm the action.

        Parameters:
        - request (HttpRequest): The HTTP request.
        - args: Additional arguments.
        - kwargs: Additional keyword arguments.

        Returns:
        - HttpResponse: A redirect to the next page URL with a success message.
        """
        messages.success(request, "You have been logged out.")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required(login_url="worker_login"), name="dispatch")
class WorkerProfileView(DetailView):
    """
    A view for displaying a worker's profile.

    Allows a customer to view a worker's profile.

    Parameters:
    - DetailView (class): Django generic view for displaying a detail page for a single object.
    """

    model = Worker
    template_name = "users/worker_profile.html"

    def get_context_data(self, **kwargs):
        """
        Returns the context data for the view.

        Adds the worker's average rating to the context.

        Parameters:
        - kwargs: Additional keyword arguments.

        Returns:
        - dict: The context data for the view.
        """
        context = super().get_context_data(**kwargs)
        worker = self.object
        rating = worker.worker_rating.aggregate(Avg("rating"))
        context["rating"] = rating["rating__avg"] or 0.0
        return context


@method_decorator(login_required(login_url="worker_login"), name="dispatch")
class WorkerProfileUpdateView(UpdateView):
    """
    A view for updating a worker's profile.

    Allows the worker to update their profile details, such as their name, email,
    phone number, and location. If the worker updates their hourly pay rate, their
    is_active flag will be set to False and the update will require admin approval.
    """

    model = Worker
    form_class = WorkerProfileUpdateForm
    template_name = "users/worker_profile_update.html"
    success_url = "/worker-profile/"

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Saves the form and sends a message to the user to confirm the profile update.
        If the worker is updating their hourly pay rate, their is_active flag will be
        set to False and the update will require admin approval.

        Parameters:
        - form (WorkerProfileUpdateForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        response = super().form_valid(form)

        # Check if hourly pay rate was updated and user is a worker
        if (
            self.request.user.is_worker
            and form.cleaned_data["hourly_rate"] != self.object.hourly_rate
        ):
            self.object.is_active = False
            self.object.save()

            # Set session flag for pending hourly pay rate approval
            self.request.session["hourly_rate_pending_approval"] = True

            # Send message to user
            messages.success(
                self.request, "Hourly pay rate updated. Pending admin approval."
            )
        else:
            messages.success(self.request, "Profile updated successfully.")

        return response
