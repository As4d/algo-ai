from django.urls import path
from .views import get_leaderboard, get_user_stats

urlpatterns = [
    path('leaderboard/', get_leaderboard, name='get_leaderboard'),
    path('stats/', get_user_stats, name='get_user_stats'),
] 