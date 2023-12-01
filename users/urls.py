from django.urls import path, include
from .views import *
from .forms import Login
from django.contrib.auth import views as authorization
from django.urls import reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    # Url using Django auth.
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', signup, name='signup'),
    path('login/',authorization.LoginView.as_view(template_name='registration/login.html', authentication_form=Login),name='login'),
    #Password reset

    #password change
    path('password_change/', CustomPasswordChangeView.as_view(),name='change_password'),
    path('delete_owner/', views.delete_owner, name="delete-owner"),
]