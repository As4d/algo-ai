from django.contrib import admin
from .models import LeaderboardEntry


@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_solved', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('user__username',)
    ordering = ('-total_solved',)
