import os

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Deletes all files from media/tmp/reports/."

    def handle(self, *args, **options):
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp', 'reports')

        if not os.path.exists(temp_dir):
            self.stdout.write(f"Directory does not exist: {temp_dir}")
            return

        removed_files = 0

        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)

            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    removed_files += 1
                    self.stdout.write(f"[DELETED] {filename}")
                except Exception as e:
                    self.stderr.write(f"[ERROR] Failed to delete {filename}: {e}")

        if removed_files == 0:
            self.stdout.write("No files to delete.")
        else:
            self.stdout.write(f"Deleted {removed_files} file(s).")
