from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class CreateUserForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def save(self, commit=True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Create a profile for the new user
            Profile.objects.create(
                user=user,
                experience_level='beginner',
                description='',
                streak=0,
                high_score_streak=0
            )
        return user
