from datetime import date, timedelta
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Category, Task
from .forms import TaskCreationForm, ProjectCreationForm, CategoryCreationForm

def filter_tasks(tasks, request):
    filter_type = request.GET.get('filter', 'all_time')
    show_completed = request.GET.get('completed', 'false') == 'true'
    
    if not show_completed:
        tasks = tasks.filter(is_completed=False)
    
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
        
    return tasks

@login_required
def index(request):
    user = request.user
    
    projects = Project.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    tasks = Task.objects.filter(user=user)
    
    tasks = filter_tasks(tasks, request)
    
    if request.method == 'POST':
        form = TaskCreationForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = user
            task.save()
            form.save_m2m()
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
        task.complete()
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
    if request.method == 'DELETE':
        project = get_object_or_404(Project, id=project_id)
        project.delete()
        return JsonResponse({'success': True, 'task_id': project_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def delete_category(request, category_id):
    if request.method == 'DELETE':
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return JsonResponse({'success': True, 'task_id': category_id})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def project_detail(request, project_id):
    user = request.user

    project = get_object_or_404(Project, pk=project_id, user=user)
    tasks = project.task_set.all()
    
    tasks = filter_tasks(tasks, request)
    
    total_tasks = tasks.count()
    
    completed_tasks = tasks.filter(is_completed=True).count()
    completed_tasks_statistics = f"Completed: {completed_tasks} / {total_tasks}"
    
    overdue_tasks = tasks.filter(is_completed=False, due_date__lt=date.today()).count()
    overdue_tasks_statistics = f"Overdue: {overdue_tasks} / {total_tasks}"
    
    context = {
        'project': project,
        'tasks': tasks,
        'completed_tasks_statistics': completed_tasks_statistics,
        'overdue_tasks_statistics': overdue_tasks_statistics
    }
    
    return render(request, 'main/project_detail.html', context)
