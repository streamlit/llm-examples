# forms.py
from django import forms
from django.contrib.auth.models import User
from api import models

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password','is_staff']

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']


class LuluTrainningForm(forms.ModelForm):
    class Meta:
        model = models.luluTrainning
        fields = ['version_title', 'attachments', 'comments']
        widgets ={
            'comments': forms.Textarea(attrs={'rows':3}),
        }