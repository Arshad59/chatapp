from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    # Url using Django auth.
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', SignUpView.as_view(), name='signup'),
    #Password reset

    #password change
    path('password_change/', CustomPasswordChangeView.as_view(),name='change_password'),
    path('delete_owner/', views.delete_owner, name="delete-owner"),
]