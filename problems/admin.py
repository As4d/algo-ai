from django.contrib import admin
from .models import Problem, UserProgress, Submission

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', 'problem_type', 'language', 'difficulty', 'order')
    list_filter = ('problem_type', 'language', 'difficulty')
    search_fields = ('name', 'description')
    ordering = ('order', 'created_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'problem_type', 'language', 'difficulty', 'order')
        }),
        ('Content', {
            'fields': ('description', 'boilerplate_code'),
            'classes': ('wide',)
        }),
        ('Test Cases', {
            'fields': ('test_cases',),
            'description': 'Enter test cases as JSON. Example: {"test1": {"input": "", "output": "Hello, World!"}}'
        }),
    )

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'is_completed', 'time_spent', 'attempts', 'last_submitted')
    list_filter = ('is_completed', 'user', 'problem')
    search_fields = ('user__username', 'problem__name')
    ordering = ('-last_submitted',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'status', 'language', 'created_at')
    list_filter = ('status', 'language', 'user', 'problem')
    search_fields = ('user__username', 'problem__name')
    ordering = ('-created_at',)
