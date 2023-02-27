from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from users.models import Customer, Worker, Skill

User = get_user_model()


class LoginForm(forms.Form):
    """
    A form for user authentication.
    """

    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)


class CustomerRegistrationForm(UserCreationForm):
    """
    A form for customer registration.
    """

    phone_number = forms.CharField(max_length=20, required=True)
    location = forms.CharField(max_length=100, required=True)

    class Meta(UserCreationForm.Meta):
        model = Customer
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "location",
            "password1",
            "password2",
        )


class CustomerProfileUpdateForm(forms.ModelForm):
    """
    A form for updating a customer's profile.
    """

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


class SkillModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    A custom form field that renders the `Skill` model choices as checkboxes.
    """

    def label_from_instance(self, obj):
        return obj.name


class WorkerRegistrationForm(UserCreationForm):
    """
    A form for worker registration.
    """

    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)
    skills = SkillModelMultipleChoiceField(
        queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple
    )
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
            "skills",
            "hourly_rate",
            "password1",
            "password2",
        ]


class WorkerProfileUpdateForm(forms.ModelForm):
    """
    A form for updating a worker's profile.
    """

    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)
    location = forms.CharField(max_length=100)
    skills = SkillModelMultipleChoiceField(
        queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple
    )
    hourly_rate = forms.FloatField()

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


class WorkerRateUpdateForm(forms.ModelForm):
    """
    A form for updating a worker's hourly rate.
    """

    hourly_rate = forms.FloatField()

    class Meta:
        model = Worker
        fields = ["hourly_rate"]


class SkillForm(forms.ModelForm):
    """
    A form for creating a new `Skill` object.
    """

    class Meta:
        model = Skill
        fields = ["name"]


class WorkerSkillsUpdateForm(forms.ModelForm):
    """
    A form for updating a worker's skills.
    """

    skills = SkillModelMultipleChoiceField(
        queryset=Skill.objects.all(), widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Worker
        fields = ["skills"]
