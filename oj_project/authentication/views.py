# authentication/views.py
from django.conf import settings
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
from .forms import SubmissionForm
from .judge import evaluate_code
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from .models import Problem
from django.conf import settings
from django.contrib.auth.decorators import login_required

# 🔑 Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
@login_required
def ai_review_view(request):
    if request.method == 'POST':
        problem_id = request.POST.get('problem_id')
        code = request.POST.get('code', '').strip()

        problem = get_object_or_404(Problem, id=problem_id)

        if code:
            prompt = f"Review the following solution for the coding problem:\n\nProblem:\n{problem.description}\n\nCode:\n{code}"
            verdict = "Accepted"  # Placeholder
            testcase_results = []  # Placeholder
            action = "ai_review"
        else:
            prompt = f"How would you approach the following coding problem?\n\n{problem.description}"
            verdict = None
            testcase_results = []
            action = "ai_review"

        ai_response = generate_gemini_response(prompt)

        return render(request, 'problem_page.html', {
            'problem': problem,
            'testcases': problem.testcases.all(),
            'ai_response': ai_response,
            'code': code,
            'verdict': verdict,
            'testcase_results': testcase_results,
            'action': action
        })

def generate_gemini_response(prompt):
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(f"Give me an breif review on this:\n{prompt}")
            return response.text
        except Exception as e:
            return f"⚠️ Error generating response: {str(e)}"


@login_required
def problem_detail_view(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    testcases = problem.testcases.all()
    verdict = None
    testcase_results = []
    summary_verdicts = []
    action = None

    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')
        action = request.POST.get('action')
        selected_testcases = testcases[:2] if action == 'run' else testcases

        all_passed = True

        for index, test in enumerate(selected_testcases):
            result_output, result_error = evaluate_code(code, language, test.input_data)
            passed = not result_error and result_output.strip() == test.expected_output.strip()

            if not passed:
                all_passed = False

            if action == 'run':
                # Full result breakdown
                testcase_results.append({
                    'number': index + 1,
                    'input': test.input_data,
                    'expected': test.expected_output,
                    'actual': result_output,
                    'error': result_error,
                    'verdict': 'Passed' if passed else 'Failed'
                })

            elif action == 'submit':
                # Minimal verdict boxes (includes hidden cases)
                summary_verdicts.append({
                    'name': f'Testcase {index + 1}',
                    'verdict': 'Passed' if passed else 'Failed'
                })

        verdict = 'Accepted' if all_passed else 'Wrong Answer'

        # Save submission for submit
        if action == 'submit':
            Submission.objects.create(
                user=request.user,
                problem=problem,
                code=code,
                language=language,
                verdict=verdict,
                output=result_output,
                error=result_error
            )

        return render(request, 'problem_page.html', {
            'problem': problem,
            'verdict': verdict,
            'testcase_results': testcase_results,
            'summary_verdicts': summary_verdicts,
            'testcases': testcases,
            'code': code,
            'language': language,
            'action': action
        })

    # ✅ Initial GET request (before any submission/run)
    return render(request, 'problem_page.html', {
        'problem': problem,
        'testcases': testcases,
        'action': 'view'
    })





@login_required
def topic_list_view(request):
    topics = Topic.objects.all()
    progress = {}

    for topic in topics:
        total = topic.problems.count()
        solved = Submission.objects.filter(
            user=request.user,
            verdict='Accepted',
            problem__topic=topic
        ).values('problem').distinct().count()
        percentage = round((solved / total) * 100) if total > 0 else 0
        progress[topic.id] = percentage

    return render(request, 'topic.html', {'topics': topics, 'progress': progress})



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
    submissions = Submission.objects.filter(user=request.user)\
        .select_related('problem')\
        .order_by('created_at')  # Ascending by time
    return render(request, 'my_submission.html', {'submissions': submissions})


@login_required
def all_submissions_view(request):
    submissions = Submission.objects.all()\
        .select_related('problem', 'user')\
        .order_by('-created_at')  # Ascending by time
    return render(request, 'submissions.html', {'submissions': submissions})




def logout_view(request):
    logout(request)
    return redirect('home')