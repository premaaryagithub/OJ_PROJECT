from django.db import models
from django.contrib.auth.models import User

LANGUAGE_CHOICES = (
    ('python', 'Python'),
    ('cpp', 'C++'),
    ('java', 'Java'),
)

class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='problems')
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"{self.problem.title} – TestCase"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='python')
    created_at = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=30, choices=[
        ('Accepted', 'Accepted'),
        ('Wrong Answer', 'Wrong Answer'),
        ('Runtime Error', 'Runtime Error'),
        ('Time Limit Exceeded', 'Time Limit Exceeded'),
        ('Compilation Error', 'Compilation Error'),
        ('Pending', 'Pending'),
    ], default='Pending')
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} – {self.problem.title} – {self.verdict}"
