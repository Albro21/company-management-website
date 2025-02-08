from django.contrib import admin
from .models import Project, Category, Task


admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Task)
