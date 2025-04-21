from django import forms
from django.forms import ModelForm
from .models import TimeEntry

class TimeEntryForm(ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['task', 'name', 'project', 'start_time', 'end_time']
