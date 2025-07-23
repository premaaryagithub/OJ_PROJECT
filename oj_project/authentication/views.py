# authentication/views.py
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import Topic, Problem, Submission
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Problem, TestCase, Submission
from .models import Topic



@login_required
def problem_detail_view(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)

    if request.method == 'POST':
        code = request.POST.get('code')
        verdict = 'Accepted'
        for test in problem.testcases.all():
            simulated_output = code.strip()  # Placeholder logic
            if simulated_output != test.expected_output.strip():
                verdict = 'Wrong Answer'
                break
        Submission.objects.create(
            user=request.user, problem=problem, code=code,
            submitted_at=timezone.now(), verdict=verdict
        )
        return render(request, 'verdict.html', {'verdict': verdict, 'problem': problem})

    return render(request, 'problem_page.html', {'problem': problem})







def topic_list_view(request):
    topics = Topic.objects.all()
    return render(request, 'topic.html', {'topics': topics})



@login_required
def problem_list_view(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    problems = topic.problems.all()[:5]  # Limit to 5 problems per topic
    return render(request, 'problem_list.html', {'topic': topic, 'problems': problems})


@login_required(login_url='login')
def welcome_page_view(request):
    return render(request, 'home.html', {'username': request.user.username})


def home_view(request):
    template = loader.get_template("base.html")
    context = {}
    return HttpResponse(template.render(context,request))

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate input
        if not username or not password:
            messages.warning(request, "Please fill in both fields.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                
                return redirect('welcome_page')  # or use reverse('welcome_page') for safety
            else:
                messages.error(request, 'Your account is inactive. Please contact admin.')
                return redirect('login')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('login')

    return render(request, 'login.html')


    # template = loader.get_template('login.html')
    # context = {}
    # return HttpResponse(template.render(context,request))

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check for missing fields
        if not username or not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
            return redirect('register')

        # Check for existing user
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Choose a different one.')
            return redirect('register')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        # Create user with hashed password
        User.objects.create_user(username=username, email=email, password=password1)
        messages.success(request, 'User created successfully. Please login.')
        return redirect('login')

    return render(request, 'register.html')


@login_required
def my_submissions_view(request):
    submissions = Submission.objects.filter(user=request.user).select_related('problem')
    return render(request, 'my_submission.html', {'submissions': submissions})

@login_required
def all_submissions_view(request):
    submissions = Submission.objects.all().select_related('problem', 'user')
    return render(request, 'submission.html', {'submissions': submissions})



def logout_view(request):
    logout(request)
    return redirect('home')