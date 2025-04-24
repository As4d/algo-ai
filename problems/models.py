from django.db import models
from django.contrib.auth.models import User

class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=10)
    description = models.TextField()  
    test_cases = models.JSONField()
    boilerplate_code = models.TextField()  
    created_at = models.DateField(auto_now_add=True)
    problem_type = models.CharField(max_length=50)
    order = models.IntegerField()

    def __str__(self):
        return self.name

class UserProgress(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    time_spent = models.IntegerField(null=True)
    attempts = models.IntegerField(null=True)
    last_submitted = models.DateField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem.name}"

class Submission(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code_submitted = models.TextField()  
    status = models.CharField(max_length=30)
    language = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.problem.name} - {self.status}"
