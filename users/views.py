
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfileUpdateForm

from django.contrib.auth.views import PasswordChangeView

from .models import CustomUser
from django.contrib.auth.models import User

def signup(request):
    if request.method=="POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
        
    form = CustomUserCreationForm()
    return render(request,"signup.html",{
        "form":form,
    })


class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy('pages:home')

def delete_owner(request):

    owner = CustomUser.objects.get(pk=request.user.pk)

    if owner:
        owner.delete()

    return redirect('pages:home')
