# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

# Local apps
from teams.decorators import employer_required
from teams.forms import CompanyForm, JobTitleForm
from teams.models import Member


@login_required
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            request.user.join_company(company)
            Member.objects.create(
                company=company,
                user=request.user,
                role=Member.Role.EMPLOYER
            )
            return redirect('teams:team') 
        
        return render(request, 'teams/create_company.html', {'form': form})
    
    else:
        form = CompanyForm()
    
    return render(request, 'teams/create_company.html', {'form': form})

@login_required
@employer_required
def settings(request):
    company = request.user.company

    company_form = CompanyForm(instance=company, prefix='company')
    job_title_form = JobTitleForm(prefix='job_title')

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'company':
            company_form = CompanyForm(request.POST, request.FILES, instance=company, prefix='company')
            if company_form.is_valid():
                company_form.save()
                messages.success(request, 'Company updated successfully.')
                return redirect('teams:settings')

        elif form_type == 'job_title':
            job_title_form = JobTitleForm(request.POST, prefix='job_title')
            if job_title_form.is_valid():
                new_job_title = job_title_form.save(commit=False)
                new_job_title.company = company
                new_job_title.save()
                messages.success(request, 'Job title added successfully.')
                return redirect('teams:settings')
            else:
                messages.error(request, 'Please correct the errors below.')

    context = {
        'company': company,
        'company_form': company_form,
        'job_title_form': job_title_form,
    }

    return render(request, 'teams/settings.html', context)

@require_http_methods(["POST"])
@login_required
def leave_company(request):
    request.user.leave_company()
    messages.success(request, "You have left the company.")
    return redirect("teams:team")

@require_http_methods(["POST"])
@login_required
@employer_required
def kick_member(request, member_id):
    member = get_object_or_404(Member, id=member_id)
    
    if request.user == member.user:
        messages.error(request, "You cannot kick yourself.")
        return redirect("teams:team")

    member.user.leave_company()
    messages.success(request, f"{member.user.full_name} was kicked from the company.")
    return redirect("teams:team")
