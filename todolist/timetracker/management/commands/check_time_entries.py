# Standard libs
from datetime import timedelta

# Django
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

# Local apps
from timetracker.models import TimeEntry


domain = getattr(settings, 'SITE_DOMAIN', '127.0.0.1')
path = reverse('timetracker:timetracker')
tracker_url = f"https://{domain}{path}"

class Command(BaseCommand):
    help = "Handles time entries running too long: sends warnings and stops if needed."

    def handle(self, *args, **options):
        now = timezone.now()
        entries = TimeEntry.objects.filter(end_time__isnull=True)

        for entry in entries:
            duration = now - entry.start_time
            user = entry.user

            if duration > timedelta(hours=23, minutes=59):
                entry.end_time = entry.start_time + timedelta(hours=23, minutes=59)
                entry.save()

                send_mail(
                    subject="Time Entry Automatically Stopped",
                    message=(
                        f"Hi {user.get_full_name()},\n\n"
                        f"Your time entry \"{entry.name}\" has automatically been stopped after reaching 24 hours.\n\n"
                        f"You can review it if needed here: {tracker_url}\n\n"
                    ),
                    from_email="no-reply@yourdomain.com",
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                self.stdout.write(f"[AUTO-STOPPED] Entry: \"{entry.name}\" | User: {user.get_full_name()} | ID: {entry.id}")

            elif duration > timedelta(hours=10):
                send_mail(
                    subject="Time Entry Running for Over 10 Hours",
                    message=(
                        f"Hi {user.get_full_name()},\n\n"
                        f"Your time entry \"{entry.name}\" has been running for over 10 hours.\n"
                        "It will automatically be stopped if it exceeds 24 hours.\n\n"
                        "Please stop it manually if you're done.\n"
                        f"You can review it if needed here: {tracker_url}"
                    ),
                    from_email="no-reply@yourdomain.com",
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                self.stdout.write(f"[WARNING] 10h+ Entry: \"{entry.name}\" | User: {user.get_full_name()} | ID: {entry.id}")
