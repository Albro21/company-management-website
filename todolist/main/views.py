from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
import json

from .models import Project, Category, Task
from .forms import TaskForm, ProjectForm, CategoryForm


def filter_tasks(tasks, request):
    filter_type = request.GET.get('filter', 'all_time')
    
    if filter_type == 'today':
        tasks = tasks.filter(due_date=date.today())
    elif filter_type == 'tomorrow':
        tasks = tasks.filter(due_date=date.today() + timedelta(days=1))
    elif filter_type == 'this_week':
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=7)
        tasks = tasks.filter(
            due_date__gte=start_of_week,
            due_date__lt=end_of_week
        )
    elif filter_type == 'next_week':
        today = date.today()
        start_of_next_week = today + timedelta(days=7 - today.weekday())
        end_of_next_week = start_of_next_week + timedelta(days=7)
        tasks = tasks.filter(
            due_date__gte=start_of_next_week,
            due_date__lt=end_of_next_week
        )
    else:
        tasks = tasks.filter(is_completed=False)

    return tasks


@login_required
def index(request):
    user = request.user
    
    tasks = user.tasks.all().order_by('is_completed', 'due_date')
    tasks = filter_tasks(tasks, request)
    
    form = TaskForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            task = form.save(commit=False)
            task.user = user
            task.save()
            form.save_m2m()
            return redirect('index')

    context = {
        'tasks': tasks,
        'form': form,
    }

    return render(request, 'main/index.html', context)


@login_required
def complete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.complete()
        return JsonResponse({'success': True, 'task_id': task_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = TaskForm(data, instance=task)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=405)


@login_required
def archive(request):
    user = request.user

    project_form = ProjectForm(request.POST or None, prefix='project')
    category_form = CategoryForm(request.POST or None, prefix='category')

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

    context = {
        'project_form': project_form,
        'category_form': category_form,
    }

    return render(request, 'main/archive.html', context)


@login_required
def delete_project(request, project_id):
    if request.method == 'DELETE':
        project = get_object_or_404(Project, id=project_id)
        project.delete()
        return JsonResponse({'success': True, 'task_id': project_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = ProjectForm(data, instance=project)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=405)


@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'errors': 'Invalid JSON'}, status=400)

        form = CategoryForm(data, instance=category)

        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'errors': 'Invalid request method'}, status=405)


@login_required
def delete_category(request, category_id):
    if request.method == 'DELETE':
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'success': True, 'task_id': category_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    tasks = project.tasks.all()
    
    tasks = filter_tasks(tasks, request)
    
    total_tasks = tasks.count()
    
    completed_tasks = tasks.filter(is_completed=True).count()
    completed_tasks_statistics = f'Completed: {completed_tasks} / {total_tasks}'
    
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=date.today()).count()
    remaining_tasks = tasks.filter(is_completed=False).count()
    
    context = {
        'project': project,
        'tasks': tasks,
        'completed_tasks_statistics': completed_tasks_statistics,
        'overdue_tasks': overdue_tasks,
        'remaining_tasks': remaining_tasks,
    }
    
    return render(request, 'main/project_detail.html', context)
