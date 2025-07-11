from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]


class UserLoginForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ["username", "password"]
