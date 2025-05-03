from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods

from datetime import date, timedelta
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
    
    tasks = user.tasks.order_by('is_completed', 'due_date')
    tasks = filter_tasks(tasks, request)
    
    form = TaskForm(request.POST or None)
    
    if request.method == 'POST':
        if request.POST.get('form_type') == 'edit_task':
            task_id = request.POST.get('task_id')
            task = get_object_or_404(Task, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('index')
        elif request.POST.get('form_type') == 'create_task':
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

@require_http_methods(["POST"])
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.complete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["POST"])
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    form = TaskForm(data, instance=task)

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors}'}, status=400)

@login_required
def archive(request):
    return render(request, 'main/archive.html')

@require_http_methods(["POST"])
@login_required
def create_project(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    project = Project.objects.create(**data, created_by=request.user)
    return JsonResponse({'success': True, 'id': project.id}, status=201)

@require_http_methods(["DELETE"])
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    project.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["PATCH"])
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    form = ProjectForm(data, instance=project)

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors}'}, status=400)

@require_http_methods(["POST"])
@login_required
def create_category(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    category = Category.objects.create(**data, user=request.user)
    return JsonResponse({'success': True, 'id': category.id}, status=201)

@require_http_methods(["DELETE"])
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    category.delete()
    return JsonResponse({'success': True}, status=200)

@require_http_methods(["PATCH"])
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    form = CategoryForm(data, instance=category)

    if form.is_valid():
        form.save()
        return JsonResponse({'success': True}, status=200)
    else:
        return JsonResponse({'success': False, 'error': f'Form contains errors: {form.errors}'}, status=400)

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id, created_by=request.user)
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
