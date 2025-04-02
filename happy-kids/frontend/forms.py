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

class questionForm(forms.ModelForm):
    class Meta:
        model = models.chat_dim_onboarding_questions
        fields = [ 'order','question_type','question', 'active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),  
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),  
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}) 
        }

class amIBoringQuestionForm(forms.ModelForm):
    class Meta:
        model = models.dim_am_i_boring_questions
        fields = [ 'order','question_type','question', 'active']
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control'}),  
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),  
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}) 
        }

class diaryForm(forms.ModelForm):
    class Meta:
        model = models.diary_facts
        fields = ['date', 'title', 'body']