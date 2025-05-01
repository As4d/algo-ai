from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

User._meta.get_field('email')._unique = True

class Profile(models.Model):
    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    experience_level = models.CharField(
        max_length=50,
        choices=EXPERIENCE_LEVELS,
        default='beginner'
    )
    description = models.CharField(max_length=500, null=True, blank=True)
    streak = models.IntegerField(default=0)
    high_score_streak = models.IntegerField(default=0)
    last_solved_date = models.DateField(null=True, blank=True)
    password_last_changed = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."

