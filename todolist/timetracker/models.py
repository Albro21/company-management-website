from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from main.models import Task, Project

class TimeEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='time_entries')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True, related_name='time_entries')
    name = models.CharField(max_length=200, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, blank=True, null=True, related_name='time_entries')
    start_time = models.DateTimeField(default=timezone.now, blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Time Entry'
        verbose_name_plural = 'Time Entries'
        ordering = ['-start_time']

    def __str__(self):
        return f"Time Entry for {self.name} ({self.start_time} - {self.end_time or 'ongoing'})"

    def clean(self):
        """Validate that end_time is after start_time."""
        if self.end_time and self.end_time < self.start_time:
            raise ValidationError("End time cannot be earlier than start time.")
        if not self.name:
            raise ValidationError("Please provide a name for the time entry.")

    @property
    def duration(self):
        """Calculate the duration of the time entry."""
        return self.end_time - self.start_time if self.end_time else timezone.now() - self.start_time

    @property
    def duration_formatted(self):
        """Calculate the duration of the time entry and return it as hh:mm:ss."""
        duration = self.duration
        hours = duration.seconds // 3600
        minutes = (duration.seconds // 60) % 60
        seconds = duration.seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def start(self):
        """Start the time entry by setting the start time."""
        if not self.start_time:
            self.start_time = timezone.now()
            self.save()

    def stop(self):
        """End the time entry by setting the end time and marking it as completed."""
        if not self.start_time:
            raise ValueError("Cannot end a time entry that hasn't started.")
        if self.end_time:
            raise ValueError("Time entry is already ended.")
        
        self.end_time = timezone.now()
        self.save()

    def update_start_time(self, new_start_time):
        """Update the start time, ensuring the new start time is before the current end time."""
        if new_start_time >= timezone.now():
            raise ValueError("Start time cannot be in the future.")
        if self.end_time and new_start_time >= self.end_time:
            raise ValueError("Start time cannot be after or equal to the end time.")
        
        self.start_time = new_start_time
        self.save()

    def update_end_time(self, new_end_time):
        """Update the end time, ensuring it's after the start time and before the current time."""
        if new_end_time >= timezone.now():
            raise ValueError("End time cannot be in the future.")
        if new_end_time <= self.start_time:
            raise ValueError("End time must be after the start time.")
        
        self.end_time = new_end_time
        self.save()
