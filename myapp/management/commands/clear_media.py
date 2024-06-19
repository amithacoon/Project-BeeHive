import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Clears the media directory'

    def handle(self, *args, **options):
        media_dir = settings.MEDIA_ROOT
        if os.path.exists(media_dir):
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to delete {file_path}. Reason: {e}'))
            self.stdout.write(self.style.SUCCESS('Media directory cleared successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Media directory does not exist.'))
