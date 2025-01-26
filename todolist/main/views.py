from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Category, Task
from .forms import TaskCreationForm, ProjectCreationForm, CategoryCreationForm


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
    user = request.user
    projects = Project.objects.filter(user=user)
    categories = Category.objects.filter(user=user)

    project_form = ProjectCreationForm(request.POST or None, prefix='project')
    category_form = CategoryCreationForm(request.POST or None, prefix='category')

    if request.method == 'POST':
        if 'submit_project' in request.POST and project_form.is_valid():
            project = project_form.save(commit=False)
            project.user = user
            project.save()
            project_form.save_m2m()
            return redirect('archive')

        if 'submit_category' in request.POST and category_form.is_valid():
            category = category_form.save(commit=False)
            category.user = user
            category.save()
            category_form.save_m2m()
            return redirect('archive')

    # Render the template
    context = {
        'project_form': project_form,
        'category_form': category_form,
        'projects': projects,
        'categories': categories,
    }
    return render(request, 'main/archive.html', context)


@login_required
def delete_project(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        project.delete()
        return JsonResponse({'success': True, 'task_id': project_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'success': True, 'task_id': category_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)