

# Register your models here.
from django.contrib import admin
from .models import Topic, Problem, TestCase, Submission

admin.site.register(Topic)
admin.site.register(Problem)
admin.site.register(TestCase)
admin.site.register(Submission)
