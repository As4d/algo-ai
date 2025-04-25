from django import forms
from django.contrib.auth.models import User
from .models import Profile

class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self, commit=True) -> User:
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Create a profile for the new user
            Profile.objects.create(
                user=user,
                experience_level='beginner',  # Default experience level
                description='',  # Empty description by default
                streak=0,
                high_score_streak=0
            )
        return user
