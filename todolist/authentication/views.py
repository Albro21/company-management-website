# Django
from django.contrib.auth import login
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

# Local apps
from .forms import CustomUserCreationForm
from teams.models import Invitation


def register(request):
    invitation = None

    if request.method == 'POST':
        invite_token = request.POST.get('invite_token')
        if invite_token:
            invitation = get_object_or_404(Invitation, token=invite_token)

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            if invitation:
                user.email = invitation.email
                user.work_email = invitation.email
                user.company = invitation.company

            user.save()

            if invitation:
                invitation.delete()

            login(request, user)
            url = reverse('teams:employee_detail', kwargs={'user_id': user.id})
            return redirect(f'{url}?tab=information')
    else:
        invite_token = request.GET.get('invite')
        if invite_token:
            invitation = get_object_or_404(Invitation, token=invite_token)
        initial_data = {'email': invitation.email} if invitation else {}
        form = CustomUserCreationForm(initial=initial_data)

    return render(request, 'registration/register.html', {
        'form': form,
        'invitation': invitation,
    })
