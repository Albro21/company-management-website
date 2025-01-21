from django import forms
from .models import Task

class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'text', 'project', 'categories', 'due_date', 'is_high_priority']
