from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class LeaderboardEntry(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_solved = models.IntegerField()
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Total Solved: {self.total_solved}"

    class Meta:
        verbose_name_plural = "Leaderboard entries"
