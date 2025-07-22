# authentication/views.py
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def home_page_view(request):
    return render(request, 'home.html', {'username': request.user.username})





def home_view(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context,request))

def login_view(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.info(request, 'User with this username does not exist')
            return redirect('/')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.info(request, 'invalid password')
            return redirect('/')

        login(request, user)
        messages.info(request, 'login successful')
        return redirect('home-page/')

    template = loader.get_template('login.html')
    context = {}
    return HttpResponse(template.render(context,request))

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.info(request, 'User with this username already exists')
            return redirect("/")

        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.save()

        messages.info(request, 'User created successfully')
        return redirect("../login/")
    template = loader.get_template("register.html")
    context = {}
    return HttpResponse(template.render(context,request))

def logout_view(request):
    logout(request)
    return redirect('home')