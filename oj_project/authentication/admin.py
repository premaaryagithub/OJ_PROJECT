

# Register your models here.
from django.contrib import admin
from .models import Topic, Problem, TestCase, Submission
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)


admin.site.register(Topic)
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
