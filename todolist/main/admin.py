from django.contrib import admin
from .models import Project, Category, Task
from django.contrib.auth.models import User
from .models import Profile


admin.site.register(Project)
admin.site.register(Category)
admin.site.register(Task)


# Custom user admin
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"

class UserAdmin(admin.ModelAdmin):
    inlines = [ProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Profile)
