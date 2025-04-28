from django.contrib import admin
from .models import Plan, PlanProblem

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'duration_days', 'difficulty', 'created_at', 'is_active')
    list_filter = ('difficulty', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'user__username')
    ordering = ('-created_at',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'description', 'duration_days', 'difficulty', 'topics')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(PlanProblem)
class PlanProblemAdmin(admin.ModelAdmin):
    list_display = ('plan', 'problem', 'order', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'plan', 'problem')
    search_fields = ('plan__name', 'problem__name')
    ordering = ('plan', 'order')
