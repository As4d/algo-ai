from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    name = models.CharField(max_length=255, unique=True)
    language = models.CharField(max_length=50)  # e.g., Python, Java
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    description = models.TextField()  # Markdown-supported question text
    test_cases = models.JSONField()  # List of input-output test cases
    boilerplate_code = models.TextField()  # Code template for the problem
    created_at = models.DateTimeField(auto_now_add=True)

    def get_markdown_description(self):
        return self.description

    def __str__(self):
        return self.name

class UserProgress(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='not_started')
    completion_time = models.IntegerField(null=True, blank=True)  # Time in milliseconds
    last_attempted = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem.name} - {self.status}"
