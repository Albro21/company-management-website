from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

from datetime import timedelta

from .models import Profile
from main.models import Category, Task

DEFAULT_CATEGORIES = [
    {'title': 'Work', 'description': 'Work-related tasks and projects', 'color': '#FF6347'},  # Tomato color
    {'title': 'Personal', 'description': 'Personal tasks and goals', 'color': '#3CB371'},  # Medium Sea Green
    {'title': 'Hobby', 'description': 'Leisure and hobby activities', 'color': '#1E90FF'},  # Dodger Blue
]

DEFAULT_TASKS = [
    {'title': 'Complete your profile', 'description': 'Fill in your details to complete your profile', 'category': 'Personal', 'is_high_priority': True},
    {'title': 'Create your first task', 'description': 'Start managing your tasks by creating your first one', 'category': 'Work', 'is_high_priority': True},
    {'title': 'Create your first category', 'description': 'Organize your tasks by creating categories', 'category': 'Personal', 'is_high_priority': False},
    {'title': 'Create your first project', 'description': 'Create your first project to group tasks and track progress', 'category': 'Work', 'is_high_priority': False},
    {'title': 'Explore the settings', 'description': 'Customize your experience by exploring the settings', 'category': 'Personal', 'is_high_priority': False},
    {'title': 'Learn how to filter tasks', 'description': 'Use filters to find and view specific tasks', 'category': 'Work', 'is_high_priority': True},
]

def create_default_categories(user):
    """Create default categories for a user if they do not exist."""
    for category_data in DEFAULT_CATEGORIES:
        Category.objects.create(
            user=user,
            title=category_data['title'],
            description=category_data['description'],
            color=category_data['color']
        )

def create_default_tasks(user):
    """Create default tasks for a user, assigning them to categories."""
    personal_category = Category.objects.get(title='Personal', user=user)
    work_category = Category.objects.get(title='Work', user=user)

    tomorrow = timezone.now().date() + timedelta(days=1)

    for task_data in DEFAULT_TASKS:
        category = personal_category if task_data['category'] == 'Personal' else work_category

        task = Task.objects.create(
            user=user,
            title=task_data['title'],
            text=task_data['description'],
            due_date=tomorrow,
            is_high_priority=task_data['is_high_priority'],
        )

        task.categories.add(category)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a profile for the user upon creation."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_defaults(sender, instance, created, **kwargs):
    """Main function to create default categories and tasks after user creation."""
    if created:  # Only create defaults for newly created users
        create_default_categories(instance)
        create_default_tasks(instance)
