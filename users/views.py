from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.views.generic import CreateView

from users.forms import CustomerRegistrationForm
from users.models import Customer

User = get_user_model()


class CustomerRegistrationView(CreateView):
    """
    A view for customer registration.

    On successful registration, sends email to customer and notification email to admin.

    """

    model = Customer
    form_class = CustomerRegistrationForm
    template_name = "users/registration_form.html"

    def form_valid(self, form):
        """
        If form is valid, create a new customer and save to the database.

        If email, username, or phone number already exists, redirect back to registration form.

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

            # Check if phone number already exists
            phone_number = form.cleaned_data["phone_number"]
            if Customer.objects.filter(phone_number=phone_number).exists():
                form.add_error("phone_number", "Phone number already exists.")
                return self.form_invalid(form)

            # Save customer to the database
            self.object = form.save(commit=False)
            self.object.is_customer = True
            self.object.save()

            # Send verification email to customer
            send_mail(
                subject="Verify your email",
                message="Please click the link below to verify your email.",
                from_email="noreply@freelancehouseholdwork.com",
                recipient_list=[self.object.email],
                fail_silently=False,
            )

            # Send notification email to admin
            send_mail(
                subject="New customer registration",
                message="A new customer has registered on Freelance Household Work. Please log in to the admin panel to approve or reject the registration request.",
                from_email="noreply@freelancehouseholdwork.com",
                recipient_list=["admin@freelancehouseholdwork.com"],
                fail_silently=False,
            )

            return redirect("users:registration_done")

        except Exception as e:
            # If an error occurs, show the registration form again
            form.add_error(None, str(e))
            return self.form_invalid(form)


class CustomerLoginView(FormView):
    """
    A view for logging in a customer.

    Allows the customer to log in to their account.

    Parameters:
    - FormView (class): Django generic view for rendering a form.
    """

    template_name = "users/customer_login.html"
    form_class = LoginForm

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

        if user and user.is_customer:
            login(self.request, user)
            messages.success(self.request, f"You are now logged in as {user.username}.")
            return redirect("customer_profile")
        else:
            messages.error(self.request, "Invalid email or password.")
            return redirect("customer_login")

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
        return redirect("customer_login")


@method_decorator(login_required(login_url="login"), name="dispatch")
class CustomerLogoutView(LogoutView):
    """
    A view for logging out a customer.

    Allows the customer to log out of their account.

    Parameters:
    - LogoutView (class): Django generic view for logging a user out.
    """

    next_page = reverse_lazy("home")

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


@method_decorator(never_cache, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class WorkerLoginView(LoginView):
    """
    A view for logging in a worker.

    Allows the worker to log in to their account.

    Parameters:
    - LoginView (class): Django generic view for logging a user in.
    """

    template_name = "users/login.html"
    form_class = LoginForm
    success_url = reverse_lazy("worker_home")

    def form_valid(self, form):
        """
        Called when a valid form is submitted.

        Logs the worker in and sends a message to confirm the action.

        Parameters:
        - form (LoginForm): The form that was submitted.

        Returns:
        - HttpResponse: A redirect to the success URL with a success message.
        """
        response = super().form_valid(form)
        messages.success(self.request, "You have been logged in.")
        return response


@method_decorator(login_required(login_url="login"), name="dispatch")
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


@method_decorator(login_required(login_url="login"), name="dispatch")
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
