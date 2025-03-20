from django.contrib import admin
from .models import Problem, UserProgress

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('name', 'problem_type', 'language', 'difficulty', 'order')
    list_filter = ('problem_type', 'language', 'difficulty')
    search_fields = ('name', 'description')
    ordering = ('problem_type', 'order', 'created_at')
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
    list_display = ('user', 'problem', 'status', 'completion_time', 'last_attempted')
    list_filter = ('status', 'user', 'problem__problem_type')
    search_fields = ('user__username', 'problem__name')
    ordering = ('-last_attempted',)
