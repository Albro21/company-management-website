from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileForm

@login_required
def settings(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()

            if 'profile_picture' in request.FILES:
                profile = request.user.profile
                profile.profile_picture = request.FILES['profile_picture']
                profile.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=request.user)

    return render(request, 'users/settings.html', {'form': form})


@login_required
def profile(request):
    tasks = request.user.task_set.all()
    total_tasks = tasks.count()
    
    completed_tasks = tasks.filter(is_completed=True).count()
    completed_tasks_statistics = f'Completed tasks: {completed_tasks} / {total_tasks}'
    
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=date.today()).count()
    remaining_tasks = tasks.filter(is_completed=False).count()
    
    context = {
        'user': request.user,
        'completed_tasks_statistics': completed_tasks_statistics,
        'overdue_tasks': overdue_tasks,
        'remaining_tasks': remaining_tasks,
    }
    
    return render(request, 'users/profile.html', context)
