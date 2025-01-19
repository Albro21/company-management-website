from collections import defaultdict
from django.shortcuts import render 
from .models import Project, Category, Task
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def index(request):
    user = request.user
    projects = Project.objects.filter(user=user)
    categories = Category.objects.all().filter(user=user)
    tasks = Task.objects.all().filter(user=user)

    context = {
        'projects': projects,
        'categories': categories,
        'tasks': tasks
    }
    
    return render(request, 'main/index.html', context)