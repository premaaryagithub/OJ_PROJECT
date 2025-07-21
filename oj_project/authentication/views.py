# authentication/views.py
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

def home_view(request):
    return render(request, 'base.html')  # Updated path

class EmailOrUsernameAuthForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Try authenticating with email or username
            self.user_cache = authenticate(
                request=self.request,
                username=username,
                password=password
            )
            
            if self.user_cache is None:
                raise forms.ValidationError(
                    "Please enter a correct email/username and password."
                )
            
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

def login_view(request):
    if request.method == 'POST':
        form = EmailOrUsernameAuthForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = EmailOrUsernameAuthForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})  # Updated path

def logout_view(request):
    logout(request)
    return redirect('home')