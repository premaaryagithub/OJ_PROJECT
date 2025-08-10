# authentication/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('welcome/',views.welcome_page_view,name='welcome_page'),
    path('topics/', views.topic_list_view, name='topics'),
    path('topics/<int:topic_id>/problems/', views.problem_list_view, name='problem_list'),
    path('problems/<int:problem_id>/', views.problem_detail_view, name='problem_detail'),
    path('submissions/', views.all_submissions_view, name='submission_list'),
    path('my-submissions/', views.my_submissions_view, name='my_submission_list'),
    path('ai-review/', views.ai_review_view, name='ai_review'),
    path('submission/<int:submission_id>/', views.submission_detail_view, name='submission_detail'),
] 
