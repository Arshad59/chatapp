from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
)
from .models import CustomUser, Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Email requied.

    def clean_email(self):
        """Checking to see if e-mail is in use."""
        if CustomUser.objects.filter(email=self.cleaned_data["email"].lower()).exists():
            raise forms.ValidationError("The given E-mail is already registered.")

        return self.cleaned_data["email"]

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"].lower()
        if commit:
            user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "username",
            "email",
            "age",
        )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "age", "password1", "password2")

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your username",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )
    age = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "placeholder": "Enter your age",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password again",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )


class Login(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter Your username",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "m-2 p-2 border-solid border-gray-300 rounded-xl",
            }
        )
    )


# Form used to update user info.
class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = CustomUser
        fields = ("username",)


# Form used to update profile info.
class ProfileUpdateForm(UserChangeForm):
    password = None

    class Meta:
        model = Profile
        fields = ["image", "bio"]
