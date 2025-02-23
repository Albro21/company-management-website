from django import forms
from .models import Project, Category, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'color']


class CategoryCreationForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'description', 'color']


class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'text', 'project', 'categories', 'due_date', 'is_high_priority']
