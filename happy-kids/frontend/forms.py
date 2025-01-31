# forms.py
from django import forms
from django.contrib.auth.models import User

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password','is_staff']

