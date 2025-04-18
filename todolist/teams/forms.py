from django import forms
from django.forms import ModelForm
from .models import Company, Role, Member

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'company_type', 'industry', 'description', 'logo', 'email', 'phone', 'website', 'address', 'city', 'country']
    
    company_type = forms.ChoiceField(
        choices=[('', 'Select a company type')] + Company.COMPANY_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=''
    )


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name']


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['role', 'rate']
