from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem

class Plan(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration_days = models.IntegerField()
    difficulty = models.CharField(max_length=15, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    problem_types = models.JSONField()  # Store list of selected problem types as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    problems = models.ManyToManyField(Problem, through='PlanProblem')
    ai_explanation = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name} Plan"

class PlanProblem(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    order = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order']
        unique_together = ['plan', 'problem']

    def __str__(self):
        return f"{self.plan.name} - {self.problem.name} (Order: {self.order})"
