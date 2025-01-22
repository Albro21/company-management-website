from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Category, Task
from .forms import TaskCreationForm


@login_required
def index(request):
    user = request.user
    
    projects = Project.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    tasks = Task.objects.filter(user=user, is_completed=False)
    
    if request.method == 'POST':
        form = TaskCreationForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = user
            task.save()
            form.save_m2m()
            return redirect('index')
    else:
        form = TaskCreationForm()

    context = {
        'projects': projects,
        'categories': categories,
        'tasks': tasks,
        'form': form,
    }

    return render(request, 'main/index.html', context)


def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.is_completed = True
        task.save()
        return JsonResponse({'success': True, 'task_id': task_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def archive(request):
    return render(request, 'main/archive.html')