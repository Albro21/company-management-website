from django import forms
from django.forms import ModelForm
from .models import *

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'company_type', 'industry', 'description', 'logo', 'email', 'phone', 'website', 'address', 'city', 'country']
    
    company_type = forms.ChoiceField(
        choices=[('', 'Select a company type')] + Company.COMPANY_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=''
    )


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = ['name']

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['type', 'start_date', 'end_date', 'reason']

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'amount', 'description', 'receipt', 'category']
